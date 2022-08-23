/**
 CreatePie() creates the pie chart for the dashboard
 */
function createPie(j){
  var payloadList = [];
  var payload = JSON.parse(j);
  console.log(j)

  for (var key of Object.keys(payload)) {
    console.log(key + "->"+ payload[key])
    payloadList.push({"name":key, "y":payload[key]})
 }
 console.log(payloadList)

  // Radialize the colors
  Highcharts.setOptions({
          colors: Highcharts.map(Highcharts.getOptions().colors, function (color) {
            return {
              radialGradient: {
                cx: 0.5,
                cy: 0.3,
                r: 0.7
              },
              stops: [
                [0, color],
                [1, Highcharts.color(color).brighten(-0.3).get('rgb')] // darken
              ]
            };
          })
        });

      const chart = Highcharts.chart('pieContainer', {
          chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
          },
          title: {
              text: ''
          },
          tooltip: {
              pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
          },
          accessibility: {
          point: {
              valueSuffix: '%'
            }
          },
          plotOptions: {
            pie: {
              allowPointSelect: true,
              cursor: 'pointer',
              dataLabels: {
              enabled: true,
              format: '<b>{point.name}</b>: {point.percentage:.1f} %',
              connectorColor: 'silver'
                }
              }
          },
          series: [{
          name: 'Share',
          data: payloadList
        }]

      });
}