"""Workflow manager orchestrating the Golazo process."""

import uuid
from datetime import datetime
from typing import Optional

from golazo_copilots.models import (
    Ticket,
    DesignDoc,
    TicketPriority,
    TicketStatus,
    WorkflowState,
)


class WorkflowManager:
    """Orchestrator for managing the Golazo workflow."""

    def __init__(self) -> None:
        self.state = WorkflowState()

    def get_workflow_state(self) -> WorkflowState:
        """Get the current workflow state."""
        return self.state

    def list_tickets(self) -> list[Ticket]:
        """List all tickets."""
        return self.state.tickets

    def get_wip_status(self) -> dict[str, int]:
        """Get current WIP status."""
        in_progress = sum(
            1 for t in self.state.tickets
            if t.status == TicketStatus.IN_PROGRESS
        )
        return {
            "current_wip": in_progress,
            "wip_limit": self.state.wip_limit,
            "available_slots": max(0, self.state.wip_limit - in_progress),
        }

    def create_ticket(
        self,
        title: str,
        description: str,
        priority: TicketPriority,
        created_by: str,
        estimated_days: Optional[float] = None,
    ) -> Ticket:
        """Create a new ticket."""
        ticket = Ticket(
            id=f"TICKET-{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            priority=priority,
            status=TicketStatus.BACKLOG,
            created_by=created_by,
            estimated_days=estimated_days,
        )
        self.state.tickets.append(ticket)
        return ticket

    def create_design_doc(
        self,
        ticket_id: str,
        title: str,
        problem_statement: str,
        proposed_solution: str,
        success_criteria: str,
        author: str,
        alternatives_considered: Optional[str] = None,
        risks: Optional[str] = None,
    ) -> DesignDoc:
        """Create a design document for a ticket."""
        ticket = self._find_ticket(ticket_id)
        
        design_doc = DesignDoc(
            id=f"DESIGN-{uuid.uuid4().hex[:8]}",
            ticket_id=ticket_id,
            title=title,
            problem_statement=problem_statement,
            proposed_solution=proposed_solution,
            success_criteria=success_criteria,
            author=author,
            alternatives_considered=alternatives_considered,
            risks=risks,
        )
        
        ticket.design_doc = design_doc
        ticket.status = TicketStatus.DESIGN_REVIEW
        ticket.updated_at = datetime.now()
        
        return design_doc

    def approve_design(self, ticket_id: str, approver: str) -> str:
        """Approve a design document."""
        ticket = self._find_ticket(ticket_id)
        
        if not ticket.design_doc:
            raise ValueError(f"Ticket {ticket_id} has no design document")
        
        if approver in ticket.design_doc.approvals:
            return f"Approver {approver} has already approved this design"
        
        ticket.design_doc.approvals.append(approver)
        ticket.design_doc.updated_at = datetime.now()
        
        # Check if we have enough approvals
        if len(ticket.design_doc.approvals) >= ticket.design_doc.required_approvals:
            ticket.status = TicketStatus.READY
            ticket.updated_at = datetime.now()
            return f"Design approved by {approver}. Ticket is now READY for implementation!"
        
        remaining = ticket.design_doc.required_approvals - len(ticket.design_doc.approvals)
        return f"Design approved by {approver}. Need {remaining} more approval(s)."

    def start_work(self, ticket_id: str, assignee: str) -> str:
        """Start work on a ticket."""
        ticket = self._find_ticket(ticket_id)
        
        # Check WIP limits
        wip_status = self.get_wip_status()
        if wip_status["available_slots"] <= 0:
            raise ValueError(
                f"WIP limit reached ({self.state.wip_limit}). "
                f"Complete existing work before starting new tickets."
            )
        
        # Ensure ticket is ready
        if ticket.status != TicketStatus.READY:
            raise ValueError(f"Ticket must be in READY status. Current status: {ticket.status}")
        
        ticket.status = TicketStatus.IN_PROGRESS
        ticket.assignee = assignee
        ticket.updated_at = datetime.now()
        
        return f"Started work on ticket {ticket_id}. Assigned to {assignee}."

    def submit_for_review(self, ticket_id: str, pr_url: str) -> str:
        """Submit work for code review."""
        ticket = self._find_ticket(ticket_id)
        
        if ticket.status != TicketStatus.IN_PROGRESS:
            raise ValueError(f"Ticket must be IN_PROGRESS. Current status: {ticket.status}")
        
        ticket.status = TicketStatus.CODE_REVIEW
        ticket.updated_at = datetime.now()
        
        return f"Ticket {ticket_id} submitted for code review. PR: {pr_url}"

    def complete_validation(self, ticket_id: str, validation_notes: str) -> str:
        """Complete customer validation and mark ticket as done."""
        ticket = self._find_ticket(ticket_id)
        
        if ticket.status != TicketStatus.CODE_REVIEW:
            raise ValueError(f"Ticket must be in CODE_REVIEW. Current status: {ticket.status}")
        
        ticket.status = TicketStatus.DONE
        ticket.validation_notes = validation_notes
        ticket.updated_at = datetime.now()
        
        return f"Ticket {ticket_id} validated and marked as DONE!"

    def get_ready_tickets(self) -> list[Ticket]:
        """Get all tickets that are ready to be picked up."""
        return [t for t in self.state.tickets if t.status == TicketStatus.READY]

    def update_wip_limit(self, limit: int) -> str:
        """Update the WIP limit."""
        if limit < 1:
            raise ValueError("WIP limit must be at least 1")
        
        old_limit = self.state.wip_limit
        self.state.wip_limit = limit
        
        return f"WIP limit updated from {old_limit} to {limit}"

    def _find_ticket(self, ticket_id: str) -> Ticket:
        """Find a ticket by ID."""
        for ticket in self.state.tickets:
            if ticket.id == ticket_id:
                return ticket
        raise ValueError(f"Ticket {ticket_id} not found")
