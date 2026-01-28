"""
Main window for the Retirement Planner application.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from models.user_profile import UserProfile, ProjectionResult
from services.retirement_calculator import RetirementCalculator
from repository.base_repository import IDataRepository


class MainWindow:
    """
    Tkinter-based main window for the Retirement Planner.
    
    Provides input fields for user financial data and displays
    retirement projection results.
    """
    
    def __init__(
        self,
        repository: IDataRepository,
        calculator: RetirementCalculator,
        on_close: Optional[Callable[[], None]] = None
    ):
        """
        Initialize the main window.
        
        Args:
            repository: Data repository for persistence
            calculator: Retirement calculator service
            on_close: Optional callback when window closes
        """
        self._repository = repository
        self._calculator = calculator
        self._on_close = on_close
        
        # Create main window
        self._root = tk.Tk()
        self._root.title("Retirement Planner")
        self._root.geometry("500x600")
        self._root.resizable(True, True)
        
        # Configure grid weights for responsiveness
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)
        
        # Create main frame with padding
        self._main_frame = ttk.Frame(self._root, padding="10")
        self._main_frame.grid(row=0, column=0, sticky="nsew")
        self._main_frame.columnconfigure(1, weight=1)
        
        # Input variables
        self._current_age_var = tk.StringVar()
        self._retirement_age_var = tk.StringVar()
        self._current_savings_var = tk.StringVar()
        self._monthly_contribution_var = tk.StringVar()
        self._desired_income_var = tk.StringVar()
        
        # Build UI
        self._create_input_section()
        self._create_button_section()
        self._create_results_section()
        
        # Load existing data
        self._load_data()
        
        # Handle window close
        self._root.protocol("WM_DELETE_WINDOW", self._handle_close)
    
    def _create_input_section(self):
        """Create the input fields section."""
        row = 0
        
        # Title
        title_label = ttk.Label(
            self._main_frame,
            text="Retirement Planner",
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=row, column=0, columnspan=2, pady=(0, 15))
        row += 1
        
        # Subtitle
        subtitle = ttk.Label(
            self._main_frame,
            text="Enter your financial information below",
            font=("Helvetica", 10)
        )
        subtitle.grid(row=row, column=0, columnspan=2, pady=(0, 15))
        row += 1
        
        # Current Age
        ttk.Label(self._main_frame, text="Current Age:").grid(
            row=row, column=0, sticky="e", padx=5, pady=5
        )
        current_age_entry = ttk.Entry(
            self._main_frame,
            textvariable=self._current_age_var,
            width=20
        )
        current_age_entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Retirement Age
        ttk.Label(self._main_frame, text="Retirement Age:").grid(
            row=row, column=0, sticky="e", padx=5, pady=5
        )
        ttk.Entry(
            self._main_frame,
            textvariable=self._retirement_age_var,
            width=20
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Current Savings
        ttk.Label(self._main_frame, text="Current Savings ($):").grid(
            row=row, column=0, sticky="e", padx=5, pady=5
        )
        ttk.Entry(
            self._main_frame,
            textvariable=self._current_savings_var,
            width=20
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Monthly Contribution
        ttk.Label(self._main_frame, text="Monthly Contribution ($):").grid(
            row=row, column=0, sticky="e", padx=5, pady=5
        )
        ttk.Entry(
            self._main_frame,
            textvariable=self._monthly_contribution_var,
            width=20
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Desired Monthly Income
        ttk.Label(self._main_frame, text="Desired Monthly Income ($):").grid(
            row=row, column=0, sticky="e", padx=5, pady=5
        )
        ttk.Entry(
            self._main_frame,
            textvariable=self._desired_income_var,
            width=20
        ).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        self._input_section_end_row = row
    
    def _create_button_section(self):
        """Create the buttons section."""
        row = self._input_section_end_row
        
        button_frame = ttk.Frame(self._main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=15)
        
        # Calculate button
        calc_button = ttk.Button(
            button_frame,
            text="Calculate",
            command=self._on_calculate
        )
        calc_button.pack(side="left", padx=5)
        
        # Save button
        save_button = ttk.Button(
            button_frame,
            text="Save",
            command=self._on_save
        )
        save_button.pack(side="left", padx=5)
        
        # Clear button
        clear_button = ttk.Button(
            button_frame,
            text="Clear",
            command=self._on_clear
        )
        clear_button.pack(side="left", padx=5)
        
        self._button_section_end_row = row + 1
    
    def _create_results_section(self):
        """Create the results display section."""
        row = self._button_section_end_row
        
        # Separator
        separator = ttk.Separator(self._main_frame, orient="horizontal")
        separator.grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        row += 1
        
        # Results title
        results_title = ttk.Label(
            self._main_frame,
            text="Projection Results",
            font=("Helvetica", 12, "bold")
        )
        results_title.grid(row=row, column=0, columnspan=2, pady=(0, 10))
        row += 1
        
        # Results frame
        self._results_frame = ttk.Frame(self._main_frame)
        self._results_frame.grid(row=row, column=0, columnspan=2, sticky="ew")
        self._results_frame.columnconfigure(1, weight=1)
        
        # Create result labels
        self._years_label = self._create_result_row(
            self._results_frame, 0, "Years to Retirement:"
        )
        self._projected_savings_label = self._create_result_row(
            self._results_frame, 1, "Projected Savings:"
        )
        self._required_nest_egg_label = self._create_result_row(
            self._results_frame, 2, "Required Nest Egg:"
        )
        self._monthly_income_label = self._create_result_row(
            self._results_frame, 3, "Monthly Income Possible:"
        )
        self._status_label = self._create_result_row(
            self._results_frame, 4, "Status:"
        )
        self._gap_label = self._create_result_row(
            self._results_frame, 5, "Surplus/Gap:"
        )
        
        # Disclaimer
        row += 1
        disclaimer = ttk.Label(
            self._main_frame,
            text="* Estimates based on 7% annual return and 4% withdrawal rate",
            font=("Helvetica", 8),
            foreground="gray"
        )
        disclaimer.grid(row=row + 1, column=0, columnspan=2, pady=(15, 0))
    
    def _create_result_row(self, parent: ttk.Frame, row: int, label_text: str) -> ttk.Label:
        """Create a row in the results section."""
        ttk.Label(parent, text=label_text).grid(
            row=row, column=0, sticky="e", padx=5, pady=3
        )
        value_label = ttk.Label(parent, text="-")
        value_label.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        return value_label
    
    def _load_data(self):
        """Load existing user data from repository."""
        try:
            profile = self._repository.load()
            if profile:
                self._current_age_var.set(str(profile.current_age))
                self._retirement_age_var.set(str(profile.retirement_age))
                self._current_savings_var.set(str(profile.current_savings))
                self._monthly_contribution_var.set(str(profile.monthly_contribution))
                self._desired_income_var.set(str(profile.desired_monthly_income))
        except Exception as e:
            messagebox.showwarning(
                "Load Warning",
                f"Could not load saved data: {e}\nStarting with empty form."
            )
    
    def _get_profile_from_inputs(self) -> Optional[UserProfile]:
        """
        Parse and validate input fields.
        
        Returns:
            UserProfile if valid, None if validation fails
        """
        try:
            current_age = int(self._current_age_var.get().strip())
            retirement_age = int(self._retirement_age_var.get().strip())
            current_savings = float(self._current_savings_var.get().strip())
            monthly_contribution = float(self._monthly_contribution_var.get().strip())
            desired_income = float(self._desired_income_var.get().strip())
            
            return UserProfile(
                current_age=current_age,
                retirement_age=retirement_age,
                current_savings=current_savings,
                monthly_contribution=monthly_contribution,
                desired_monthly_income=desired_income
            )
        except ValueError as e:
            error_msg = str(e)
            if "invalid literal" in error_msg:
                messagebox.showerror(
                    "Input Error",
                    "Please enter valid numbers in all fields."
                )
            else:
                messagebox.showerror("Validation Error", error_msg)
            return None
    
    def _on_calculate(self):
        """Handle Calculate button click."""
        profile = self._get_profile_from_inputs()
        if not profile:
            return
        
        result = self._calculator.calculate(profile)
        self._display_results(result)
    
    def _display_results(self, result: ProjectionResult):
        """Update the results display with calculated values."""
        self._years_label.config(text=f"{result.years_to_retirement} years")
        self._projected_savings_label.config(
            text=f"${result.projected_savings:,.2f}"
        )
        self._required_nest_egg_label.config(
            text=f"${result.required_nest_egg:,.2f}"
        )
        self._monthly_income_label.config(
            text=f"${result.monthly_income_possible:,.2f}"
        )
        
        # Status with color
        if result.is_on_track:
            self._status_label.config(text="? On Track!", foreground="green")
        else:
            self._status_label.config(text="? Not on Track", foreground="red")
        
        # Surplus/Gap
        if result.surplus_or_gap >= 0:
            self._gap_label.config(
                text=f"Surplus: ${result.surplus_or_gap:,.2f}",
                foreground="green"
            )
        else:
            self._gap_label.config(
                text=f"Gap: ${abs(result.surplus_or_gap):,.2f}",
                foreground="red"
            )
    
    def _on_save(self):
        """Handle Save button click."""
        profile = self._get_profile_from_inputs()
        if not profile:
            return
        
        try:
            self._repository.save(profile)
            messagebox.showinfo("Saved", "Your data has been saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save data: {e}")
    
    def _on_clear(self):
        """Handle Clear button click."""
        self._current_age_var.set("")
        self._retirement_age_var.set("")
        self._current_savings_var.set("")
        self._monthly_contribution_var.set("")
        self._desired_income_var.set("")
        
        # Clear results
        self._years_label.config(text="-")
        self._projected_savings_label.config(text="-")
        self._required_nest_egg_label.config(text="-")
        self._monthly_income_label.config(text="-")
        self._status_label.config(text="-", foreground="black")
        self._gap_label.config(text="-", foreground="black")
    
    def _handle_close(self):
        """Handle window close event - save data before closing."""
        # Try to save if there's valid data
        profile = self._get_profile_from_inputs()
        if profile:
            try:
                self._repository.save(profile)
            except Exception:
                pass  # Silent fail on close
        
        if self._on_close:
            self._on_close()
        
        self._root.destroy()
    
    def run(self):
        """Start the main event loop."""
        self._root.mainloop()
