import { Component, Input, OnInit, OnChanges, SimpleChanges, OnDestroy, HostListener } from '@angular/core';
import {Chart, ChartConfiguration, registerables} from 'chart.js';
import {ContenerComponent} from '../contener/contener.component';
import {H1Component} from '../texts/h1/h1.component';
import {getGradient} from '../../../utils/utils';


Chart.register(...registerables);

@Component({
  selector: 'app-chart',
  imports: [
    ContenerComponent,
    H1Component
  ],
  standalone : true,
  templateUrl: './chart.component.html',
  styleUrl: './chart.component.scss'
})
export class ChartComponent implements OnInit, OnChanges, OnDestroy {
  @Input() chartData: any = null;
  
  config : ChartConfiguration = {
    type: 'line',
    data : {
      labels: ['jan','fev','mar','avr','mai','jun','jul','aou','sep','oct','nov','dec'],
      datasets: [
        {
          label: 'Collecte mensuelle',
          data: [0,0,0,0,0,0,0,0,0,0,0,0],
          fill: true,
          borderColor: "rgba(12, 82, 156, 1)",
          tension: 0.1,
        }
      ]
    },
    options : {
      responsive: true,
      maintainAspectRatio: false,
      backgroundColor :function(context : any) {
        const chart = context.chart;
        const {ctx, chartArea} = chart;

        if (!chartArea) {
          return;
        }
        return getGradient(ctx, chartArea);
      },
      aspectRatio : 3,
      scales : {
        y : {
          min : 0,
          border : {
            display : false
          },
        },
        x : {
          border : {
            display : false
          },
          grid : {
            display : false,
          }
        }
      },
      plugins: {
        legend: {
          display: true
        }
      }
    }
  };
  chart : any;
  private resizeObserver?: ResizeObserver;
  
  ngOnInit(){
    // Attendre que le DOM soit prêt
    setTimeout(() => {
      this.chart = new Chart("Chart", this.config);
      if (this.chartData) {
        this.updateChart();
      }
      this.setupResizeObserver();
    }, 100);
  }
  
  ngOnChanges(changes: SimpleChanges): void {
    if (changes['chartData'] && this.chart && this.chartData) {
      this.updateChart();
    }
  }
  
  ngOnDestroy(): void {
    if (this.chart) {
      this.chart.destroy();
    }
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
  }
  
  @HostListener('window:resize', ['$event'])
  onResize(): void {
    if (this.chart) {
      this.chart.resize();
    }
  }
  
  setupResizeObserver(): void {
    const canvas = document.getElementById('Chart');
    if (canvas && 'ResizeObserver' in window) {
      this.resizeObserver = new ResizeObserver(() => {
        if (this.chart) {
          this.chart.resize();
        }
      });
      this.resizeObserver.observe(canvas);
    }
  }
  
  updateChart(): void {
    if (this.chart && this.chartData && this.chartData.datasets && this.chartData.datasets.length > 0) {
      if (this.chartData.labels) {
        this.chart.data.labels = this.chartData.labels;
      }
      if (this.chartData.datasets[0] && this.chartData.datasets[0].data) {
        this.chart.data.datasets[0].data = this.chartData.datasets[0].data;
        
        // Ajuster l'échelle Y dynamiquement
        const maxValue = Math.max(...this.chartData.datasets[0].data, 1);
        this.chart.options.scales.y.max = maxValue * 1.2;
      }
      
      this.chart.update('none'); // 'none' pour éviter l'animation qui peut causer des problèmes
    }
  }
}
