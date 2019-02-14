function alpha() {
    d3.json(`/DSP_Data`).then(function(data) {
  
      //console.log(data)
      var Day = []
      var Predicted = []
      console.log(data)

      for (var i=0; i< data.length; i++) {
        Day.push(data[i]['Days']);
        Predicted.push(data[i]['Predicted']);
      }      

      //console.log(Day)
      //console.log(Predicted)

      var Prediction = {
        x: Day,
        y: Predicted,
        type: 'scatter',
        name: 'Regression',
        line: {
          color: 'teal',
        }

        
      };

      d3.json(`/TickTock`).then(function(data2) {
  
        //console.log(data)
        var Day_2= []
        var Real = []
        console.log(data2)
  
        for (var i=0; i< data2.length; i++) {
          Day_2.push(data2[i]['Days']);
          Real.push(data2[i]['Real Values']);
        }      
  
        //console.log(Day)
        //console.log(Predicted)
  
        var Reality = {
          x: Day_2,
          y: Real,
          type: 'scatter',
          name: 'Reality',
          line: {
            color: 'black',
          }
  
        };

        var updatemenus = [
          {
            buttons: [
              {
                args: [{ 'visible': [true, false] },
                { 'title': 'Regression' }],
                label: 'Prediction',
                method: 'update'
              },
              {
                args: [{ 'visible': [false, true] },
                { 'title': 'Reality' }],
                label: 'Reality',
                method: 'update'
              },
              {
                args: [{ 'visible': [true, true] },
                { 'title': 'Regression vs Reality' }],
                label: 'Reset',
                method: 'update'
              }
            ],
            direction: 'left',
            pad: { 'r': 10, 't': 10 },
            showactive: true,
            type: 'buttons',
            x: 0.1,
            xanchor: 'left',
            y: 1.2,
            yanchor: 'top'
          },
    
        ]
Data = [Prediction, Reality]

var layout = {
  title:'Signal Based Regression vs Reality'
};

    
    
      Plotly.newPlot('myDiv', Data, layout); } ) })}



 alpha()
 