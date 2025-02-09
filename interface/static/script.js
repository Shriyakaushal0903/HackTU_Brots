document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("loanForm").addEventListener("submit", function (event) {
      event.preventDefault();

      const loanData = {
          Loan_ID: document.getElementById("loan_id").value,
          Gender: document.getElementById("gender").value,
          Married: document.getElementById("married").value,
          Dependents: document.getElementById("dependents").value,
          Education: document.getElementById("education").value,
          Self_Employed: document.getElementById("self_employed").value,
          ApplicantIncome: parseInt(document.getElementById("applicant_income").value),
          CoapplicantIncome: parseInt(document.getElementById("coapplicant_income").value) || 0,
          LoanAmount: parseInt(document.getElementById("loan_amount").value),
          Loan_Amount_Term: parseInt(document.getElementById("loan_term").value),
          Credit_History: parseInt(document.getElementById("credit_history").value),
          Property_Area: document.getElementById("property_area").value
      };

      fetch('/loan_approval', {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(loanData)
      })
      .then(response => response.json())
      .then(data => {
          const resultDiv = document.getElementById("result");
          resultDiv.style.display = "block";
          document.getElementById("approval_status").textContent = data.approval_status;
      })
      .catch(error => console.error("Error:", error));
  });
});
