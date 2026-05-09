document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".treeview li.collapsible > :not(ul)").forEach((treeview) => {
    treeview.addEventListener("click", (event) => {
      event.stopPropagation();
      const li = event.target.closest("li.collapsible");
      li.classList.toggle("collapsed");
    }
  )});
});
