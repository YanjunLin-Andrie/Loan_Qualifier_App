# -*- coding: utf-8 -*-
"""Loan Qualifier Application.

This is a command line interface application to match applicants with qualifying loans.

Example:
    $ python app.py
"""
# Import all necessary libraries to be used later
import sys
import fire
import questionary
from pathlib import Path

# Import functions to be used later
from qualifier.utils.fileio import load_csv, save_csv
from qualifier.utils.calculators import (
    calculate_monthly_debt_ratio,
    calculate_loan_to_value_ratio,
)
from qualifier.filters.max_loan_size import filter_max_loan_size
from qualifier.filters.credit_score import filter_credit_score
from qualifier.filters.debt_to_income import filter_debt_to_income
from qualifier.filters.loan_to_value import filter_loan_to_value

# This function is used to get a list of banking data from a CSV file, which the file path is given by the user
def load_bank_data():
    """Ask for the file path to the latest banking data and load the CSV file.

    Returns:
        The bank data from the data rate sheet CSV file.
    """
    # Prompt the path question to the user
    csvpath = questionary.text("Enter a file path to a rate-sheet (.csv):").ask()
    csvpath = Path(csvpath)
    # If the path given by user doesn't exist:
    if not csvpath.exists():
        # Deliver the following message and exit out of the program
        sys.exit(f"Oops! Can't find this path: {csvpath}")
    # Path correct and able to load and use the bank data list
    return load_csv(csvpath)

# Use CLI to interact with the user to obtain their financial information. Such as credit score, current debt, monthly income, and etc.
def get_applicant_info():
    """Prompt dialog to get the applicant's financial information.

    Returns:
        Returns the applicant's financial information.
    """
    credit_score = questionary.text("What's your credit score?").ask()
    debt = questionary.text("What's your current amount of monthly debt?").ask()
    income = questionary.text("What's your total monthly income?").ask()
    loan_amount = questionary.text("What's your desired loan amount?").ask()
    home_value = questionary.text("What's your home value?").ask()

    # Convert the information provided by the user to data types that are required for later use in find_qualifiying_loans function 
    credit_score = int(credit_score)
    debt = float(debt)
    income = float(income)
    loan_amount = float(loan_amount)
    home_value = float(home_value)

    return credit_score, debt, income, loan_amount, home_value

# Based on information provided in the bank list and by the user in correct data type, determine qualifying loans for the user
def find_qualifying_loans(bank_data, credit_score, debt, income, loan, home_value):
    """Determine which loans the user qualifies for.

    Loan qualification criteria is based on:
        - Credit Score
        - Loan Size
        - Debit to Income ratio (calculated)
        - Loan to Value ratio (calculated)

    Args:
        bank_data (list): A list of bank data.
        credit_score (int): The applicant's current credit score.
        debt (float): The applicant's total monthly debt payments.
        income (float): The applicant's total monthly income.
        loan (float): The total loan amount applied for.
        home_value (float): The estimated home value.

    Returns:
        A list of the banks willing to underwrite the loan.

    """
    # Calculate the monthly debt ratio
    monthly_debt_ratio = calculate_monthly_debt_ratio(debt, income)
    print(f"The monthly debt to income ratio is {monthly_debt_ratio:.02f}")

    # Calculate loan to value ratio
    loan_to_value_ratio = calculate_loan_to_value_ratio(loan, home_value)
    print(f"The loan to value ratio is {loan_to_value_ratio:.02f}.")

    # Run qualification filters
    bank_data_filtered = filter_max_loan_size(loan, bank_data)
    bank_data_filtered = filter_credit_score(credit_score, bank_data_filtered)
    bank_data_filtered = filter_debt_to_income(monthly_debt_ratio, bank_data_filtered)
    bank_data_filtered = filter_loan_to_value(loan_to_value_ratio, bank_data_filtered)

    # Display numbers of qualifying loans for the user
    print(f"Found {len(bank_data_filtered)} qualifying loans")

    return bank_data_filtered

    
# This function will allow the user to save the generated loan list into a CSV file under the path of their choice in a CLI environment
def save_qualifying_loans(qualifying_loans):
    """Saves the qualifying loans to a CSV file.

    Args:
        qualifying_loans (list of lists): The qualifying bank loans.
    """
    # Ask for the file path to save the qualified loans list to a CSV file.
    output_path = questionary.text("Please enter a file path to save qualified loans to a csv file: ").ask()
    output_path = Path(output_path)
    return save_csv(output_path,qualifying_loans)

# This function integrates the entire application and puts everything together for the user
def run():
    """The main function for running the script."""

    # Load the latest Bank data
    bank_data = load_bank_data()

    # Get the applicant's information
    credit_score, debt, income, loan_amount, home_value = get_applicant_info()

    # Find qualifying loans
    qualifying_loans = find_qualifying_loans(
        bank_data, credit_score, debt, income, loan_amount, home_value
    )

    # Provide the user options to save qualifying loans if there are qualifying loans
    # If there are at least one qualifying loan from the filtered list
    if qualifying_loans != []:
        # Provide options to the user to save or not save the loans list by letting them choos Y or N.
        save = questionary.confirm("Do you want to save the list of qualifying loans?: ").ask()
        # If the user want to save the file:
        if save == True:
            # Save qualifying loans function will be put in use
            save_qualifying_loans(qualifying_loans)
            # Deliver a message to inform the user that the result can be find at the location of their choice
            sys.exit("Please find the result list at the location of your choice. Thank you for using the Loan Qualifier!")
        # If the user doesn't want to save the list:
        else:
            # Deliver the message of "Thank you" and exit the program
            sys.exit("Thank you for using the Loan Qualifier!")
    # If there isn't any qualifying loan from the filtered list:
    else:
        # Deliver the message that "Can't find qualified loans", and exit.
        sys.exit("Can't find any qualified loans. Thank you for using the Loan Qualifier!")


if __name__ == "__main__":
    fire.Fire(run)
