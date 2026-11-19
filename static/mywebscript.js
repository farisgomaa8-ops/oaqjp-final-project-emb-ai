let RunSentimentAnalysis = () => {
    const textToAnalyze = document.getElementById("textToAnalyze").value;
    const resultElement = document.getElementById("system_response");
    const xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function () {
        if (this.readyState === 4) {
            if (this.status === 200 || this.status === 503) {
                resultElement.textContent = this.responseText;
            } else {
                resultElement.textContent = "Unable to analyze text. Please try again.";
            }
        }
    };

    xhttp.open(
        "GET",
        "emotionDetector?textToAnalyze=" + encodeURIComponent(textToAnalyze),
        true
    );
    xhttp.send();
};

