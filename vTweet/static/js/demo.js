$(document).ready(function () {

  function clearQuery() {
    var queryField = document.getElementById('query')
    queryField.value = ''
  }

  $("#clearBox").click(function () {
    clearQuery();
  });
});