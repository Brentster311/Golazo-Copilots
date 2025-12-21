"""Example workflows demonstrating Golazo process automation."""

import asyncio
from golazo_copilots.orchestrator import WorkflowOrchestrator, WorkflowManager


async def example_complete_feature_workflow():
    """Example: Complete feature development workflow."""
    wm = WorkflowManager()
    orchestrator = WorkflowOrchestrator(wm)
    
    # First, create a ticket manually to get the ID
    ticket = wm.create_ticket(
        title="Add user profile page",
        description="Create a user profile page with avatar and bio",
        priority="planned",
        created_by="alice",
        estimated_days=5.0
    )
    
    # Now create workflow for the rest
    workflow = orchestrator.create_workflow(
        name="Feature Development Workflow",
        description="Complete workflow from design to validation",
        steps=[
            {
                "name": "create_design",
                "description": "Create design document",
                "action": "create_design_doc",
                "parameters": {
                    "ticket_id": ticket.id,
                    "title": "User Profile Page Design",
                    "problem_statement": "Users need a way to view and edit their profile",
                    "proposed_solution": "Create /profile route with avatar upload and bio editing",
                    "success_criteria": "Users can view profile, upload avatar, and edit bio",
                    "author": "alice",
                    "risks": "Avatar upload may need size limits and validation"
                }
            },
            {
                "name": "first_approval",
                "description": "First peer approval",
                "action": "approve_design",
                "parameters": {
                    "ticket_id": ticket.id,
                    "approver": "bob"
                },
                "dependencies": ["create_design"]
            },
            {
                "name": "second_approval",
                "description": "Second peer approval",
                "action": "approve_design",
                "parameters": {
                    "ticket_id": ticket.id,
                    "approver": "charlie"
                },
                "dependencies": ["first_approval"]
            },
            {
                "name": "start_implementation",
                "description": "Start working on the feature",
                "action": "start_work",
                "parameters": {
                    "ticket_id": ticket.id,
                    "assignee": "alice"
                },
                "dependencies": ["second_approval"]
            },
            {
                "name": "submit_review",
                "description": "Submit code for review",
                "action": "submit_for_review",
                "parameters": {
                    "ticket_id": ticket.id,
                    "pr_url": "https://github.com/org/repo/pull/456"
                },
                "dependencies": ["start_implementation"]
            },
            {
                "name": "validation",
                "description": "Complete customer validation",
                "action": "complete_validation",
                "parameters": {
                    "ticket_id": ticket.id,
                    "validation_notes": "Tested with 5 users, all successfully uploaded avatars and updated bios"
                },
                "dependencies": ["submit_review"]
            }
        ]
    )
    
    print(f"Created workflow: {workflow.id}")
    print(f"Ticket ID: {ticket.id}")
    
    # Execute the workflow
    result = await orchestrator.execute_workflow(workflow.id, actor="alice")
    
    print("\nWorkflow completed!")
    print(f"Status: {result['status']}")
    print("\nAudit trail:")
    for log in result['audit_logs']:
        print(f"  {log['timestamp']}: {log['step_name']} - {log['status']}")
    
    return result


async def example_basic_workflow():
    """Example: Basic ticket creation and design approval."""
    wm = WorkflowManager()
    
    print("=== Creating a ticket ===")
    ticket = wm.create_ticket(
        title="Fix login bug",
        description="Login fails when username has special characters",
        priority="interrupt",
        created_by="bob",
        estimated_days=1.0
    )
    print(f"Created: {ticket.id} - {ticket.title}")
    
    print("\n=== Creating design document ===")
    design = wm.create_design_doc(
        ticket_id=ticket.id,
        title="Login Bug Fix Design",
        problem_statement="Special characters in username cause login to fail",
        proposed_solution="Add input sanitization before authentication check",
        success_criteria="Users with special characters in username can login",
        author="bob"
    )
    print(f"Design created: {design.id}")
    
    print("\n=== Getting approvals (need 2) ===")
    result1 = wm.approve_design(ticket.id, "alice")
    print(result1)
    
    result2 = wm.approve_design(ticket.id, "charlie")
    print(result2)
    
    print("\n=== Checking ready tickets ===")
    ready = wm.get_ready_tickets()
    print(f"Ready tickets: {[t.id for t in ready]}")
    
    print("\n=== Starting work ===")
    result = wm.start_work(ticket.id, "bob")
    print(result)
    
    print("\n=== WIP Status ===")
    wip = wm.get_wip_status()
    print(f"Current WIP: {wip['current_wip']}/{wip['wip_limit']}")
    print(f"Available slots: {wip['available_slots']}")
    
    return ticket


async def example_wip_limit_enforcement():
    """Example: WIP limit enforcement."""
    wm = WorkflowManager()
    
    print("=== Testing WIP Limits ===")
    print(f"Initial WIP limit: {wm.state.wip_limit}")
    
    # Create and prepare multiple tickets
    tickets = []
    for i in range(5):
        ticket = wm.create_ticket(
            title=f"Task {i+1}",
            description=f"Description for task {i+1}",
            priority="planned",
            created_by="alice"
        )
        
        # Create and approve design
        wm.create_design_doc(
            ticket_id=ticket.id,
            title=f"Design {i+1}",
            problem_statement="Problem",
            proposed_solution="Solution",
            success_criteria="Criteria",
            author="alice"
        )
        wm.approve_design(ticket.id, "bob")
        wm.approve_design(ticket.id, "charlie")
        
        tickets.append(ticket)
    
    print(f"\nCreated {len(tickets)} ready tickets")
    
    # Try to start work on tickets (should hit WIP limit)
    started = 0
    for ticket in tickets:
        try:
            wm.start_work(ticket.id, "alice")
            started += 1
            print(f"✓ Started work on {ticket.id}")
        except ValueError as e:
            print(f"✗ Cannot start {ticket.id}: {e}")
    
    print(f"\nSuccessfully started: {started}/{len(tickets)}")
    
    wip = wm.get_wip_status()
    print(f"Final WIP: {wip['current_wip']}/{wip['wip_limit']}")


if __name__ == "__main__":
    print("=" * 60)
    print("Example 1: Basic Workflow")
    print("=" * 60)
    asyncio.run(example_basic_workflow())
    
    print("\n" + "=" * 60)
    print("Example 2: WIP Limit Enforcement")
    print("=" * 60)
    asyncio.run(example_wip_limit_enforcement())
    
    print("\n" + "=" * 60)
    print("Example 3: Complete Feature Workflow with Orchestrator")
    print("=" * 60)
    asyncio.run(example_complete_feature_workflow())
