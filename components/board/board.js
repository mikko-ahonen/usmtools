htmx.onLoad(function (content) {
  console.log("FOO");
  htmx.logAll();
  content.querySelectorAll(".sortable-tasks").forEach(function (sortable) {
    console.log("found sortable task");
    new Sortable(sortable, {
      forceFallback: true,
      animation: 0,
      group: "tasks",
      chosenClass: "sortable-chosen",
      ghostClass: "sortable-ghost",
      dragClass: "sortable-drag",
      onChoose: function(e) {
        e.target.classList.add('grabbing');
      },
      onUnchoose: function(e) {
        e.target.classList.remove('grabbing');
      },
      onStart: function(e) {
        e.target.classList.add('grabbing');
      },
      onMove: function(e) {
        e.target.classList.add('grabbing');
      },
      onEnd: function (event) {
        event.target.classList.remove('grabbing');
        htmx.ajax("POST", "{% url 'boards:task_move' tenant_id board.board_type board.uuid %}", {
          target: "#board",
          swap: "outerHTML",
          values: {
            from_list: event.from.closest(".list").id,
            to_list: event.to.closest(".list").id,
            item: event.item.id,
            task_uuids: Array.from(event.to.querySelectorAll(".task")).map(div => div.id)
          }
        })
      }
    })
  })

  content.querySelectorAll(".sortable-lists").forEach(function (sortable) {
    console.log("found sortable list");
    new Sortable(sortable, {
      forceFallback: true,
      animation: 0,
      group: "lists",
      handle: ".list-handle",
      ghostClass: "sortable-ghost",
      dragClass: "none",
      onEnd: function (event) {
        htmx.ajax("POST", "{% url 'boards:list_move' tenant_id board.board_type board.uuid %}", {
          target: "#board",
          swap: "outerHTML",
          values: {
            list_uuids: Array.from(content.querySelectorAll(".sortable-lists .list")).map(div => div.id)
          }
        })
      }
    }) 
  })
})
