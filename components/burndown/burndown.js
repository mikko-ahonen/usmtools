function sumArrayUpTo(arrData, index) {
    var total = 0;
    for (var i = 0; i <= index; i++) {
        if (arrData.length > i) {
            total += arrData[i];
        }
    }
    return total;
}

function showBurnDown(elementId, labels, burndownData, idealData) {

    var speedCanvas = document.getElementById(elementId);

    //Chart.defaults.global.defaultFontFamily = "Arial";
    //Chart.defaults.global.defaultFontSize = 14;

    const totalHoursInSprint = burndownData[0];
    const idealHoursPerDay = totalHoursInSprint / 9;
    i = 0;

    var speedData = {
        labels: labels,
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
                data: idealData,
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
