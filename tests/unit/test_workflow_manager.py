"""Unit tests for WorkflowManager."""

import pytest
from golazo_copilots.orchestrator import WorkflowManager
from golazo_copilots.models import TicketPriority, TicketStatus


class TestTicketCreation:
    """Tests for ticket creation."""

    def test_create_ticket(self):
        """Test creating a basic ticket."""
        wm = WorkflowManager()
        ticket = wm.create_ticket(
            title="Test ticket",
            description="Test description",
            priority=TicketPriority.PLANNED,
            created_by="alice",
        )

        assert ticket.title == "Test ticket"
        assert ticket.description == "Test description"
        assert ticket.priority == TicketPriority.PLANNED
        assert ticket.created_by == "alice"
        assert ticket.status == TicketStatus.BACKLOG
        assert ticket.id.startswith("TICKET-")

    def test_create_ticket_with_estimate(self):
        """Test creating a ticket with time estimate."""
        wm = WorkflowManager()
        ticket = wm.create_ticket(
            title="Test ticket",
            description="Test description",
            priority=TicketPriority.PLANNED,
            created_by="alice",
            estimated_days=5.0,
        )

        assert ticket.estimated_days == 5.0


class TestDesignDoc:
    """Tests for design document management."""

    def test_create_design_doc(self):
        """Test creating a design document."""
        wm = WorkflowManager()
        ticket = wm.create_ticket(
            title="Test ticket",
            description="Test description",
            priority=TicketPriority.PLANNED,
            created_by="alice",
        )

        design_doc = wm.create_design_doc(
            ticket_id=ticket.id,
            title="Test Design",
            problem_statement="Problem to solve",
            proposed_solution="Solution approach",
            success_criteria="Success definition",
            author="alice",
        )

        assert design_doc.title == "Test Design"
        assert design_doc.problem_statement == "Problem to solve"
        assert design_doc.author == "alice"
        assert len(design_doc.approvals) == 0
        assert ticket.status == TicketStatus.DESIGN_REVIEW

    def test_approve_design_single(self):
        """Test single design approval."""
        wm = WorkflowManager()
        ticket = wm.create_ticket(
            title="Test ticket",
            description="Test description",
            priority=TicketPriority.PLANNED,
            created_by="alice",
        )
        wm.create_design_doc(
            ticket_id=ticket.id,
            title="Test Design",
            problem_statement="Problem",
            proposed_solution="Solution",
            success_criteria="Criteria",
            author="alice",
        )

        result = wm.approve_design(ticket.id, "bob")

        assert "bob" in ticket.design_doc.approvals
        assert ticket.status == TicketStatus.DESIGN_REVIEW  # Still in review
        assert "Need 1 more approval" in result

    def test_approve_design_complete(self):
        """Test completing design approval."""
        wm = WorkflowManager()
        ticket = wm.create_ticket(
            title="Test ticket",
            description="Test description",
            priority=TicketPriority.PLANNED,
            created_by="alice",
        )
        wm.create_design_doc(
            ticket_id=ticket.id,
            title="Test Design",
            problem_statement="Problem",
            proposed_solution="Solution",
            success_criteria="Criteria",
            author="alice",
        )

        wm.approve_design(ticket.id, "bob")
        result = wm.approve_design(ticket.id, "charlie")

        assert len(ticket.design_doc.approvals) == 2
        assert ticket.status == TicketStatus.READY
        assert "now READY" in result

    def test_approve_design_duplicate(self):
        """Test duplicate approval from same person."""
        wm = WorkflowManager()
        ticket = wm.create_ticket(
            title="Test ticket",
            description="Test description",
            priority=TicketPriority.PLANNED,
            created_by="alice",
        )
        wm.create_design_doc(
            ticket_id=ticket.id,
            title="Test Design",
            problem_statement="Problem",
            proposed_solution="Solution",
            success_criteria="Criteria",
            author="alice",
        )

        wm.approve_design(ticket.id, "bob")
        result = wm.approve_design(ticket.id, "bob")

        assert "already approved" in result
        assert len(ticket.design_doc.approvals) == 1


class TestWIPLimits:
    """Tests for WIP limit enforcement."""

    def test_start_work_within_limit(self):
        """Test starting work within WIP limit."""
        wm = WorkflowManager()
        ticket = self._create_ready_ticket(wm)

        result = wm.start_work(ticket.id, "alice")

        assert ticket.status == TicketStatus.IN_PROGRESS
        assert ticket.assignee == "alice"
        assert "Started work" in result

    def test_start_work_exceeds_limit(self):
        """Test WIP limit enforcement."""
        wm = WorkflowManager()
        wm.update_wip_limit(2)

        # Create and start 2 tickets (at limit)
        for i in range(2):
            ticket = self._create_ready_ticket(wm)
            wm.start_work(ticket.id, "alice")

        # Try to start a third (should fail)
        ticket3 = self._create_ready_ticket(wm)
        with pytest.raises(ValueError, match="WIP limit reached"):
            wm.start_work(ticket3.id, "alice")

    def test_wip_status(self):
        """Test WIP status reporting."""
        wm = WorkflowManager()
        wm.update_wip_limit(3)

        ticket1 = self._create_ready_ticket(wm)
        ticket2 = self._create_ready_ticket(wm)

        wm.start_work(ticket1.id, "alice")
        wm.start_work(ticket2.id, "bob")

        wip_status = wm.get_wip_status()

        assert wip_status["current_wip"] == 2
        assert wip_status["wip_limit"] == 3
        assert wip_status["available_slots"] == 1

    def test_update_wip_limit(self):
        """Test updating WIP limit."""
        wm = WorkflowManager()

        result = wm.update_wip_limit(5)

        assert wm.state.wip_limit == 5
        assert "updated from 3 to 5" in result

    def _create_ready_ticket(self, wm):
        """Helper: create a ticket in READY state."""
        ticket = wm.create_ticket(
            title="Test ticket",
            description="Test description",
            priority=TicketPriority.PLANNED,
            created_by="alice",
        )
        wm.create_design_doc(
            ticket_id=ticket.id,
            title="Test Design",
            problem_statement="Problem",
            proposed_solution="Solution",
            success_criteria="Criteria",
            author="alice",
        )
        wm.approve_design(ticket.id, "bob")
        wm.approve_design(ticket.id, "charlie")
        return ticket


class TestWorkflowProgression:
    """Tests for ticket workflow progression."""

    def test_submit_for_review(self):
        """Test submitting work for review."""
        wm = WorkflowManager()
        ticket = self._create_in_progress_ticket(wm)

        result = wm.submit_for_review(ticket.id, "https://github.com/org/repo/pull/1")

        assert ticket.status == TicketStatus.CODE_REVIEW
        assert "submitted for code review" in result

    def test_complete_validation(self):
        """Test completing customer validation."""
        wm = WorkflowManager()
        ticket = self._create_in_review_ticket(wm)

        result = wm.complete_validation(ticket.id, "Validated with customers")

        assert ticket.status == TicketStatus.DONE
        assert ticket.validation_notes == "Validated with customers"
        assert "marked as DONE" in result

    def test_get_ready_tickets(self):
        """Test getting ready tickets."""
        wm = WorkflowManager()

        # Create some tickets in different states
        ready1 = self._create_ready_ticket(wm, "Ready 1")
        ready2 = self._create_ready_ticket(wm, "Ready 2")
        backlog = wm.create_ticket(
            title="Backlog", description="", priority=TicketPriority.PLANNED, created_by="alice"
        )

        ready_tickets = wm.get_ready_tickets()

        assert len(ready_tickets) == 2
        assert ready1 in ready_tickets
        assert ready2 in ready_tickets
        assert backlog not in ready_tickets

    def _create_ready_ticket(self, wm, title="Test ticket"):
        """Helper: create a ticket in READY state."""
        ticket = wm.create_ticket(
            title=title,
            description="Test description",
            priority=TicketPriority.PLANNED,
            created_by="alice",
        )
        wm.create_design_doc(
            ticket_id=ticket.id,
            title="Test Design",
            problem_statement="Problem",
            proposed_solution="Solution",
            success_criteria="Criteria",
            author="alice",
        )
        wm.approve_design(ticket.id, "bob")
        wm.approve_design(ticket.id, "charlie")
        return ticket

    def _create_in_progress_ticket(self, wm):
        """Helper: create a ticket in IN_PROGRESS state."""
        ticket = self._create_ready_ticket(wm)
        wm.start_work(ticket.id, "alice")
        return ticket

    def _create_in_review_ticket(self, wm):
        """Helper: create a ticket in CODE_REVIEW state."""
        ticket = self._create_in_progress_ticket(wm)
        wm.submit_for_review(ticket.id, "https://github.com/org/repo/pull/1")
        return ticket
