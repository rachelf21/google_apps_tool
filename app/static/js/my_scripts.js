function convert_date(date) {
  try {
    var newDate = new Date(date);
    const ye = new Intl.DateTimeFormat("en", { year: "numeric" }).format(newDate);
    const mo = new Intl.DateTimeFormat("en", { month: "short" }).format(newDate);
    const da = new Intl.DateTimeFormat("en", { day: "2-digit" }).format(newDate);
    const hr = new Intl.DateTimeFormat("en", {
      hour: "numeric",
      minute: "numeric",
    }).format(newDate);
    return ye + " " + mo + " " + da + "&nbsp;&nbsp;" + hr;
  } catch (err) {
    return "00:00:00";
  }
}

function load_data() {
  console.log("load data");
}

function convert_date_no_time(date) {
  try {
    var newDate = new Date(date);
    const ye = new Intl.DateTimeFormat("en", { year: "numeric" }).format(newDate);
    const mo = new Intl.DateTimeFormat("en", { month: "short" }).format(newDate);
    const da = new Intl.DateTimeFormat("en", { day: "2-digit" }).format(newDate);

    return ye + " " + mo + " " + da;
  } catch (err) {
    return "NA";
  }
}

function fixedEncodeURIComponent(str) {
  return encodeURIComponent(str).replace(/[!'()*]/g, function (c) {
    return "%" + c.charCodeAt(0).toString(16);
  });
}

function toggle(source) {
  checkboxes = document.getElementsByName("download_checkbox");
  for (var i = 0, n = checkboxes.length; i < n; i++) checkboxes[i].checked = source.checked;
}

function download_selected() {
  var base_url;
  var file_name;
  //console.log("download selected");
  var filenames = document.getElementsByName("filenames");
  var boxes = document.getElementsByName("download_checkbox");
  for (var i = 0; i < boxes.length; i++) {
    //console.log(boxes[i].id);
    //console.log(filenames[i].id);
    base_url = boxes[i].id;
    file_name = filenames[i].id;
    if (boxes[i].checked) {
      //console.log(boxes[i].checked);
      download_photo(base_url, file_name);
    }
  }
}
function download(file_id, file_name, mime_type) {
  console.log("download function " + file_id + " " + file_name + " " + mime_type);
  //var text = "/download_file/" + file_id + "/" + file_name+"/"+fixedEncodeURIComponent(mime_type);
  var text = "/download_file/" + file_id + "/" + file_name + "/" + mime_type.replace("/", "12345");
  //var text = "/download_file/" + file_id + "/" + "blah";

  if (confirm("You are about to download " + file_name + ". Continue?")) window.location.href = text;
  //window.location.href = text;
}

function download_photo(base_url, file_name) {
  //console.log("download function: " + base_url + "/" + file_name);
  var text = "/download_photo/" + base_url.replace(/\//g, "12345") + "/" + file_name;

  //if (confirm("You are about to download " + file_name + ". Continue?")) window.location.href = text;
  window.location.href = text;
}
