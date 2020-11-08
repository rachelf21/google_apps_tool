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
    return ye + " " + mo + " " + da + "&nbsp; &nbsp; &nbsp;" + hr;
  } catch (err) {
    return "00:00:00";
  }
}
