"""Advanced orchestrator for multi-step Golazo workflows."""

import json
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from pydantic import BaseModel, Field

from golazo_copilots.orchestrator.workflow_manager import WorkflowManager


class WorkflowStepStatus(str, Enum):
    """Status of a workflow step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStep(BaseModel):
    """A step in a workflow."""
    name: str
    description: str
    action: str  # Tool or action to execute
    parameters: dict[str, Any] = Field(default_factory=dict)
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    dependencies: list[str] = Field(default_factory=list)  # Names of steps that must complete first


class WorkflowPolicy(BaseModel):
    """Policy rules for workflow execution."""
    require_design_approval: bool = True
    enforce_wip_limits: bool = True
    require_code_review: bool = True
    require_validation: bool = True
    min_design_approvals: int = 2
    max_parallel_steps: int = 3


class WorkflowAuditLog(BaseModel):
    """Audit log entry for workflow actions."""
    timestamp: datetime = Field(default_factory=datetime.now)
    workflow_id: str
    step_name: str
    action: str
    actor: str
    status: str
    details: dict[str, Any] = Field(default_factory=dict)


class Workflow(BaseModel):
    """A multi-step workflow."""
    id: str
    name: str
    description: str
    steps: list[WorkflowStep]
    policy: WorkflowPolicy = Field(default_factory=WorkflowPolicy)
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    audit_logs: list[WorkflowAuditLog] = Field(default_factory=list)


class WorkflowOrchestrator:
    """Orchestrator for complex multi-step workflows with policy enforcement."""

    def __init__(self, workflow_manager: WorkflowManager) -> None:
        self.workflow_manager = workflow_manager
        self.workflows: dict[str, Workflow] = {}
        self.action_handlers: dict[str, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Register default action handlers."""
        self.action_handlers = {
            "create_ticket": self._handle_create_ticket,
            "create_design_doc": self._handle_create_design_doc,
            "approve_design": self._handle_approve_design,
            "start_work": self._handle_start_work,
            "submit_for_review": self._handle_submit_for_review,
            "complete_validation": self._handle_complete_validation,
        }

    def create_workflow(self, name: str, description: str, steps: list[dict]) -> Workflow:
        """Create a new workflow."""
        workflow_steps = [WorkflowStep(**step) for step in steps]
        
        workflow = Workflow(
            id=f"WF-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            description=description,
            steps=workflow_steps,
        )
        
        self.workflows[workflow.id] = workflow
        return workflow

    async def execute_workflow(self, workflow_id: str, actor: str) -> dict[str, Any]:
        """Execute a workflow with policy enforcement."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow.status = "running"
        results = []

        # Execute steps respecting dependencies
        completed_steps = set()
        
        while len(completed_steps) < len(workflow.steps):
            # Find steps that can be executed (dependencies met)
            executable_steps = [
                step for step in workflow.steps
                if step.status == WorkflowStepStatus.PENDING
                and all(dep in completed_steps for dep in step.dependencies)
            ]

            if not executable_steps:
                # Check if we're stuck
                pending_steps = [
                    step for step in workflow.steps
                    if step.status == WorkflowStepStatus.PENDING
                ]
                if pending_steps:
                    workflow.status = "failed"
                    raise ValueError(
                        f"Workflow stuck. Pending steps: {[s.name for s in pending_steps]}"
                    )
                break

            # Execute eligible steps (respecting parallel limit)
            for step in executable_steps[:workflow.policy.max_parallel_steps]:
                try:
                    result = await self._execute_step(workflow, step, actor)
                    results.append(result)
                    completed_steps.add(step.name)
                except Exception as e:
                    step.status = WorkflowStepStatus.FAILED
                    step.error = str(e)
                    workflow.status = "failed"
                    raise

        workflow.status = "completed"
        workflow.updated_at = datetime.now()

        return {
            "workflow_id": workflow_id,
            "status": workflow.status,
            "results": results,
            "audit_logs": [log.model_dump() for log in workflow.audit_logs],
        }

    async def _execute_step(
        self, workflow: Workflow, step: WorkflowStep, actor: str
    ) -> dict[str, Any]:
        """Execute a single workflow step."""
        step.status = WorkflowStepStatus.IN_PROGRESS
        step.started_at = datetime.now()

        # Log the action
        audit_log = WorkflowAuditLog(
            workflow_id=workflow.id,
            step_name=step.name,
            action=step.action,
            actor=actor,
            status="started",
            details=step.parameters,
        )
        workflow.audit_logs.append(audit_log)

        try:
            # Get the handler for this action
            handler = self.action_handlers.get(step.action)
            if not handler:
                raise ValueError(f"No handler for action: {step.action}")

            # Execute the action
            result = handler(step.parameters)
            
            step.status = WorkflowStepStatus.COMPLETED
            step.result = result
            step.completed_at = datetime.now()

            # Log completion
            completion_log = WorkflowAuditLog(
                workflow_id=workflow.id,
                step_name=step.name,
                action=step.action,
                actor=actor,
                status="completed",
                details={"result": result},
            )
            workflow.audit_logs.append(completion_log)

            return {"step": step.name, "status": "completed", "result": result}

        except Exception as e:
            step.status = WorkflowStepStatus.FAILED
            step.error = str(e)
            
            # Log failure
            failure_log = WorkflowAuditLog(
                workflow_id=workflow.id,
                step_name=step.name,
                action=step.action,
                actor=actor,
                status="failed",
                details={"error": str(e)},
            )
            workflow.audit_logs.append(failure_log)
            
            raise

    def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
        """Get the status of a workflow."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        return {
            "id": workflow.id,
            "name": workflow.name,
            "status": workflow.status,
            "steps": [
                {
                    "name": step.name,
                    "status": step.status,
                    "result": step.result,
                    "error": step.error,
                }
                for step in workflow.steps
            ],
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
        }

    def get_audit_logs(self, workflow_id: str) -> list[dict[str, Any]]:
        """Get audit logs for a workflow."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        return [log.model_dump() for log in workflow.audit_logs]

    # Action handlers
    def _handle_create_ticket(self, params: dict[str, Any]) -> str:
        """Handle ticket creation."""
        ticket = self.workflow_manager.create_ticket(**params)
        return f"Created ticket {ticket.id}"

    def _handle_create_design_doc(self, params: dict[str, Any]) -> str:
        """Handle design doc creation."""
        design_doc = self.workflow_manager.create_design_doc(**params)
        return f"Created design doc {design_doc.id}"

    def _handle_approve_design(self, params: dict[str, Any]) -> str:
        """Handle design approval."""
        return self.workflow_manager.approve_design(**params)

    def _handle_start_work(self, params: dict[str, Any]) -> str:
        """Handle starting work."""
        return self.workflow_manager.start_work(**params)

    def _handle_submit_for_review(self, params: dict[str, Any]) -> str:
        """Handle code review submission."""
        return self.workflow_manager.submit_for_review(**params)

    def _handle_complete_validation(self, params: dict[str, Any]) -> str:
        """Handle validation completion."""
        return self.workflow_manager.complete_validation(**params)
