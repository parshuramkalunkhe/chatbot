// Example POST method implementation:
async function postData(url = "", data = {}) {
    // Default options are marked with *
    const response = await fetch(url, {
        method: "POST", headers: {
            "Content-Type": "application/json",
            // 'Content-Type': 'application/x-www-form-urlencoded',
        }, body: JSON.stringify(data), // body data type must match "Content-Type" header
    });
    return response.json(); // parses JSON response into native JavaScript objects
}




var inputTxt = document.getElementById("input-text");
var sendBtn = document.getElementById("send");
var question = document.getElementById("que");
var solution = document.getElementById("sol");

sendBtn.addEventListener("click", async () => {
    var inputValue = inputTxt.value
    inputTxt.value = "";
    document.querySelector(".message").style.display = "block";
    question.innerHTML = inputValue;
    let result = await postData("/api", {"input": inputValue});
    solution.innerHTML = result.result
});