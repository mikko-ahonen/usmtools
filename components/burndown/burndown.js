function sumArrayUpTo(arrData, index) {
    var total = 0;
    for (var i = 0; i <= index; i++) {
        if (arrData.length > i) {
            total += arrData[i];
        }
    }
    return total;
}

function showBurnDown(elementId, burndownData, scopeChange = []) {

    var speedCanvas = document.getElementById(elementId);

    //Chart.defaults.global.defaultFontFamily = "Arial";
    //Chart.defaults.global.defaultFontSize = 14;

    const totalHoursInSprint = burndownData[0];
    const idealHoursPerDay = totalHoursInSprint / 9;
    i = 0;

    var speedData = {
        labels: [ "Day 1",	"Day 2",	"Day 3",	"Day 4",	"Day 5",	"Day 6",	"Day 7",	"Day 8",	"Day 9", "Day 10"],
        datasets: [
            {
                label: "Burndown",
                data: burndownData,
                fill: false,
                borderColor: "#EE6868",
                backgroundColor: "#EE6868",
                lineTension: 0,
          },
          {
                label: "Ideal",
                borderColor: "#6C8893",
                backgroundColor: "#6C8893",
                lineTension: 0,
                borderDash: [5, 5],
                fill: false,
                data: [
                    Math.round(totalHoursInSprint - (idealHoursPerDay * i++) + sumArrayUpTo(scopeChange, 0)), // 1
                    Math.round(totalHoursInSprint - (idealHoursPerDay * i++) + sumArrayUpTo(scopeChange, 1)), // 2
                    Math.round(totalHoursInSprint - (idealHoursPerDay * i++) + sumArrayUpTo(scopeChange, 2)), // 3
                    Math.round(totalHoursInSprint - (idealHoursPerDay * i++) + sumArrayUpTo(scopeChange, 3)), // 4
                    Math.round(totalHoursInSprint - (idealHoursPerDay * i++) + sumArrayUpTo(scopeChange, 4)), // 5
                    Math.round(totalHoursInSprint - (idealHoursPerDay * i++) + sumArrayUpTo(scopeChange, 5)), // 6
                    Math.round(totalHoursInSprint - (idealHoursPerDay * i++) + sumArrayUpTo(scopeChange, 6)), // 7
                    Math.round(totalHoursInSprint - (idealHoursPerDay * i++) + sumArrayUpTo(scopeChange, 7)), // 8
                    Math.round(totalHoursInSprint - (idealHoursPerDay * i++) + sumArrayUpTo(scopeChange, 8)), // 9
                    Math.round(totalHoursInSprint - (idealHoursPerDay * i++) + sumArrayUpTo(scopeChange, 9))  // 10
                ]
          },
        ]
      };

      var chartOptions = {
        legend: {
          display: true,
          position: 'top',
          labels: {
            boxWidth: 80,
            fontColor: 'black'
          }
        },
        scales: {
            yAxes: [{
                ticks: {
                    min: 0,
                    max: Math.round(burndownData[0] * 1.1)
                }
            }]
        }
      };

      var lineChart = new Chart(speedCanvas, {
        type: 'line',
        data: speedData,
        options: chartOptions
      });
}

/*
document.body.addEventListener("updateChart", function(evt){
    //showBurnDown("burndown", burndownData, idealData);
});
*/
