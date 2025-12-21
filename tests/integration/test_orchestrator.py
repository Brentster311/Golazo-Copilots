"""Integration tests for WorkflowOrchestrator."""

import pytest
from golazo_copilots.orchestrator import WorkflowOrchestrator, WorkflowManager
from golazo_copilots.models import TicketStatus


@pytest.mark.asyncio
async def test_complete_workflow_execution():
    """Test executing a complete workflow from start to finish."""
    wm = WorkflowManager()
    orchestrator = WorkflowOrchestrator(wm)
    
    # Create initial ticket
    ticket = wm.create_ticket(
        title="Test Feature",
        description="Test feature description",
        priority="planned",
        created_by="alice"
    )
    
    # Create workflow
    workflow = orchestrator.create_workflow(
        name="Complete Feature Workflow",
        description="Test workflow",
        steps=[
            {
                "name": "create_design",
                "description": "Create design doc",
                "action": "create_design_doc",
                "parameters": {
                    "ticket_id": ticket.id,
                    "title": "Test Design",
                    "problem_statement": "Problem",
                    "proposed_solution": "Solution",
                    "success_criteria": "Criteria",
                    "author": "alice"
                }
            },
            {
                "name": "approve_1",
                "description": "First approval",
                "action": "approve_design",
                "parameters": {
                    "ticket_id": ticket.id,
                    "approver": "bob"
                },
                "dependencies": ["create_design"]
            },
            {
                "name": "approve_2",
                "description": "Second approval",
                "action": "approve_design",
                "parameters": {
                    "ticket_id": ticket.id,
                    "approver": "charlie"
                },
                "dependencies": ["approve_1"]
            },
            {
                "name": "start_work",
                "description": "Start implementation",
                "action": "start_work",
                "parameters": {
                    "ticket_id": ticket.id,
                    "assignee": "alice"
                },
                "dependencies": ["approve_2"]
            },
            {
                "name": "submit_review",
                "description": "Submit for review",
                "action": "submit_for_review",
                "parameters": {
                    "ticket_id": ticket.id,
                    "pr_url": "https://github.com/test/pr/1"
                },
                "dependencies": ["start_work"]
            },
            {
                "name": "complete",
                "description": "Complete validation",
                "action": "complete_validation",
                "parameters": {
                    "ticket_id": ticket.id,
                    "validation_notes": "All tests passed"
                },
                "dependencies": ["submit_review"]
            }
        ]
    )
    
    # Execute workflow
    result = await orchestrator.execute_workflow(workflow.id, actor="alice")
    
    # Verify results
    assert result["status"] == "completed"
    assert len(result["results"]) == 6
    assert ticket.status == TicketStatus.DONE
    assert len(result["audit_logs"]) == 12  # 2 logs per step (start + complete)


@pytest.mark.asyncio
async def test_workflow_with_parallel_steps():
    """Test workflow with steps that can run in parallel."""
    wm = WorkflowManager()
    orchestrator = WorkflowOrchestrator(wm)
    
    # Create multiple tickets
    ticket1 = wm.create_ticket(
        title="Feature 1",
        description="Description 1",
        priority="planned",
        created_by="alice"
    )
    ticket2 = wm.create_ticket(
        title="Feature 2",
        description="Description 2",
        priority="planned",
        created_by="bob"
    )
    
    # Create workflow with parallel steps (no dependencies)
    workflow = orchestrator.create_workflow(
        name="Parallel Workflow",
        description="Test parallel execution",
        steps=[
            {
                "name": "design_1",
                "description": "Design for ticket 1",
                "action": "create_design_doc",
                "parameters": {
                    "ticket_id": ticket1.id,
                    "title": "Design 1",
                    "problem_statement": "Problem 1",
                    "proposed_solution": "Solution 1",
                    "success_criteria": "Criteria 1",
                    "author": "alice"
                }
            },
            {
                "name": "design_2",
                "description": "Design for ticket 2",
                "action": "create_design_doc",
                "parameters": {
                    "ticket_id": ticket2.id,
                    "title": "Design 2",
                    "problem_statement": "Problem 2",
                    "proposed_solution": "Solution 2",
                    "success_criteria": "Criteria 2",
                    "author": "bob"
                }
            }
        ]
    )
    
    # Execute workflow
    result = await orchestrator.execute_workflow(workflow.id, actor="alice")
    
    # Verify both steps completed
    assert result["status"] == "completed"
    assert len(result["results"]) == 2
    assert ticket1.design_doc is not None
    assert ticket2.design_doc is not None


@pytest.mark.asyncio
async def test_workflow_audit_logging():
    """Test that workflow execution creates proper audit logs."""
    wm = WorkflowManager()
    orchestrator = WorkflowOrchestrator(wm)
    
    ticket = wm.create_ticket(
        title="Test Ticket",
        description="Test",
        priority="planned",
        created_by="alice"
    )
    
    workflow = orchestrator.create_workflow(
        name="Test Workflow",
        description="Test audit logging",
        steps=[
            {
                "name": "create_design",
                "description": "Create design",
                "action": "create_design_doc",
                "parameters": {
                    "ticket_id": ticket.id,
                    "title": "Design",
                    "problem_statement": "Problem",
                    "proposed_solution": "Solution",
                    "success_criteria": "Criteria",
                    "author": "alice"
                }
            }
        ]
    )
    
    await orchestrator.execute_workflow(workflow.id, actor="alice")
    
    # Check audit logs
    logs = orchestrator.get_audit_logs(workflow.id)
    assert len(logs) == 2  # started + completed
    
    started_log = logs[0]
    assert started_log["step_name"] == "create_design"
    assert started_log["action"] == "create_design_doc"
    assert started_log["actor"] == "alice"
    assert started_log["status"] == "started"
    
    completed_log = logs[1]
    assert completed_log["status"] == "completed"


@pytest.mark.asyncio
async def test_workflow_status_tracking():
    """Test workflow status tracking throughout execution."""
    wm = WorkflowManager()
    orchestrator = WorkflowOrchestrator(wm)
    
    ticket = wm.create_ticket(
        title="Test",
        description="Test",
        priority="planned",
        created_by="alice"
    )
    
    workflow = orchestrator.create_workflow(
        name="Status Test",
        description="Test status",
        steps=[
            {
                "name": "step1",
                "description": "Step 1",
                "action": "create_design_doc",
                "parameters": {
                    "ticket_id": ticket.id,
                    "title": "Design",
                    "problem_statement": "Problem",
                    "proposed_solution": "Solution",
                    "success_criteria": "Criteria",
                    "author": "alice"
                }
            }
        ]
    )
    
    # Check initial status
    initial_status = orchestrator.get_workflow_status(workflow.id)
    assert initial_status["status"] == "pending"
    
    # Execute
    await orchestrator.execute_workflow(workflow.id, actor="alice")
    
    # Check final status
    final_status = orchestrator.get_workflow_status(workflow.id)
    assert final_status["status"] == "completed"
    assert final_status["steps"][0]["status"] == "completed"
