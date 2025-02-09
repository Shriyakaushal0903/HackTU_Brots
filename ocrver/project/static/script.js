// /static/js/script.js
function handleUpload() {
  const fileInput = document.getElementById("fileInput");
  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append("file", file);

  fetch("/upload", {
      method: "POST",
      body: formData,
  })
  .then(response => response.json())
  .then(result => {
      if (result.match_found) {
          document.getElementById("output").innerHTML = "<pre>" + JSON.stringify(result.matched_record, null, 2) + "</pre>";
      } else {
          document.getElementById("output").innerHTML = "No match found in the database.";
      }
  })
  .catch(error => {
      document.getElementById("output").innerHTML = "Error: " + error;
  });
}
