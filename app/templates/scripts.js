var addentry = document.getElementById("addentry");

function submitForm() {
	form.submit();
}
function overBudget() {
	if (overBudget)
		{alert("You are currently over the budget")}
}

addentry.addEventListener(submitForm());