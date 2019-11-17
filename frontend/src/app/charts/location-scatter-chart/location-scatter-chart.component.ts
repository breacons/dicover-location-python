import { Component, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { Chart } from 'chart.js';

@Component({
  selector: 'app-location-scatter-chart',
  templateUrl: './location-scatter-chart.component.html',
  styleUrls: ['./location-scatter-chart.component.scss']
})
export class LocationScatterChartComponent implements OnInit {
  chart: any;
  @ViewChild('myChart', { static: true }) private chartRef;

  constructor() {}

  ngOnInit() {
    /* Chart.helpers.extend(Chart.controllers.scatter.prototype, {
      fireSliderEvent: function(point, canvas, boundingRect) {
        const mouseX = Math.round(
          (((boundingRect.left + point._view.x) /
            (boundingRect.right - boundingRect.left)) *
            canvas.width) /
            this.chart.chart.currentDevicePixelRatio
        );
        const mouseY = Math.round(
          (((boundingRect.top + point._view.y) /
            (boundingRect.bottom - boundingRect.top)) *
            canvas.height) /
            this.chart.chart.currentDevicePixelRatio
        );
        const oEvent = document.createEvent('MouseEvents');
        oEvent.initMouseEvent(
          'click',
          true,
          true,
          document.defaultView,
          0,
          mouseX,
          mouseY,
          mouseX,
          mouseY,
          false,
          false,
          false,
          false,
          0,
          canvas
        );
        canvas.dispatchEvent(oEvent);
      },
      highlightPoints: function(point) {
        var canvas = this.chart.chart.canvas;
        var boundingRect = canvas.getBoundingClientRect();
        var points = this.getDataset().metaData;
        this.fireSliderEvent(points[point], canvas, boundingRect);
      }
    }); */

    this.chart = new Chart(this.chartRef.nativeElement, {
      type: 'bubble',
      data: {
        labels: [], // your labels array
        datasets: []
      },
      options: {
        animation: {
          duration: 2000,
          easing: 'linear'
        },
        legend: {
          display: false
        },
        scales: {
          xAxes: [
            {
              display: false,
              ticks: {
                min: 60.1855,
                max: 60.1864
              }
            }
          ],
          yAxes: [
            {
              display: false,
              ticks: {
                min: 24.8225,
                max: 24.826
              }
            }
          ]
        }
      }
    });
    // setInterval(() => this.updateData(), 300);
  }

  setChartData(data: any) {
    this.chart.data.datasets = data;
    this.chart.update();
  }
  updateData(lookupTableOfUpdates: any) {
    let deleteCount = 0;
    this.chart.data.datasets.forEach(dataset => {
      dataset.data = dataset.data.map(data => {
        if (!!data && data.id && !!lookupTableOfUpdates[data.id]) {
          const newData = lookupTableOfUpdates[data.id];
          lookupTableOfUpdates[data.id] = null;
          delete lookupTableOfUpdates[data.id];
          deleteCount += 1;
          // dataset.controller.highlightPoints(0);
          return newData;
        }
        return data;
      });
    });
    // Add nodes that are new
    const dataSetsToAdd = [];
    if (lookupTableOfUpdates && this.chart.data.datasets) {
      Object.keys(lookupTableOfUpdates).map(key => {
        const userUpdate = lookupTableOfUpdates[key];
        if (!!userUpdate) {
          console.log(userUpdate.r)
          dataSetsToAdd.push({
            data: [
              {
                x: userUpdate.latitude,
                y: userUpdate.longitude,
                id: userUpdate.id,
                r: userUpdate.r
              }
            ],
            borderColor: '#' + userUpdate.team,
            backgroundColor: '#' + userUpdate.team,
            fill: true,
            teamId: userUpdate.team
          });
        }
      });
    }

    this.chart.data.datasets = [...this.chart.data.datasets, ...dataSetsToAdd];

    this.chart.update();
    // this.selectPoint('');
  }

  selectPoint(id: string) {
    console.log(this.chart.getDatasetMeta(0));
  }
}
