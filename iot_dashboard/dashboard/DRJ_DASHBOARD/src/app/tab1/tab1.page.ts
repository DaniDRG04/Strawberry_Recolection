import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  IonContent, IonHeader, IonToolbar, IonGrid, IonRow, IonTitle, IonCol,
  IonCard, IonCardSubtitle, IonCardHeader, IonCardTitle, IonCardContent
} from '@ionic/angular/standalone';
import { ExploreContainerComponent } from '../explore-container/explore-container.component';

import {
  Chart, LineController, CategoryScale, LinearScale, PointElement,
  LineElement, Title, Tooltip, Legend, ChartConfiguration
} from 'chart.js';

// Register everything needed for a line chart
Chart.register(LineController, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

@Component({
  selector: 'app-tab1',
  templateUrl: 'tab1.page.html',
  styleUrls: ['tab1.page.scss'],
  standalone: true,
  imports: [
    IonContent,
    IonGrid,
    IonRow,
    IonCol,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    ExploreContainerComponent,
    IonTitle,
    IonToolbar,
    IonHeader,
    IonCardSubtitle,
    CommonModule
  ],
})
export class Tab1Page {
  imageUrl: string | null = null;

  temperature: number | null = null;
  humidity: number | null = null;
  soilMoisture: number | null = null;
  lightIntensity: number | null = null;
  date: string | null = null;
  date_img: string | null = null;


  chart: Chart | null = null;

  constructor() {}

  ionViewWillEnter() {
    this.loadData();
  }

  ngOnDestroy() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
  }

  ionViewWillLeave() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
  }

  // Convert base64 → image
  base64ToImage(base64: string) {
    this.imageUrl = `data:image/png;base64,${base64}`;
  }

  // Fetch data from Flask backend
// Fetch data from Flask backend
// Fetch data from Flask backend
async loadData() {
  try {
    const res = await fetch('http://10.25.15.228:5000/alldata');
    const data = await res.json();

    // Extract sensorData and images
    const sensorData = data.sensorData || [];
    const images = data.images || [];

    // Convert strings to Date and filter last 24h
    const now = new Date();
    const last24h = sensorData.filter((entry: any) => {
      const entryTime = new Date(entry.date_time);
      return entryTime >= new Date(now.getTime() - 24 * 60 * 60 * 1000);
    });

    // Last sensor values (latest entry)
    const lastSensor = sensorData.length > 0 ? sensorData[sensorData.length - 1] : null;
    if (lastSensor) {
      console.log('Last Sensor Data:', lastSensor);
      this.date = lastSensor.date_time;
      this.temperature = lastSensor.temp_air;
      this.humidity = lastSensor.hum_air;
      this.soilMoisture = lastSensor.hum_soil;
      this.lightIntensity = lastSensor.light;
      console.log('data:', lastSensor);
    }

    // Last image (latest entry)
    const lastImage = images.length > 0 ? images[images.length - 1] : null;
    if (lastImage) {
      console.log('Last Image Data:', lastImage);
      this.date_img = lastImage.date_time;
      this.base64ToImage(lastImage.image_base64);
    }

    // Prepare chart data
    const labels = last24h.map((e: any) => new Date(e.date_time).toLocaleTimeString());
    const temperatureData = last24h.map((e: any) => e.temp_air);
    const humidityData = last24h.map((e: any) => e.hum_air);
    const soilData = last24h.map((e: any) => e.hum_soil);
    const lightData = last24h.map((e: any) => e.light);

    // Create chart
    this.createChart(labels, temperatureData, humidityData, soilData, lightData);

  } catch (error) {
    console.error('Error loading dashboard data:', error);
  }
}



  // Create chart dynamically
  createChart(labels: string[], temperatureData: number[], humidityData: number[], soilData: number[], lightData: number[]) {
    const ctx = document.getElementById('sensorChart') as HTMLCanvasElement;

    if (this.chart) {
      this.chart.destroy();
    }

    this.chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Temperature (°C)',
            data: temperatureData,
            borderColor: 'red',
            backgroundColor: 'rgba(255,0,0,0.2)',
            fill: false,
            tension: 0.3
          },
          {
            label: 'Humidity (%)',
            data: humidityData,
            borderColor: 'blue',
            backgroundColor: 'rgba(0,0,255,0.2)',
            fill: false,
            tension: 0.3
          },
          {
            label: 'Soil Moisture (%)',
            data: soilData,
            borderColor: 'green',
            backgroundColor: 'rgba(0,255,0,0.2)',
            fill: false,
            tension: 0.3
          },
          {
            label: 'Light Intensity',
            data: lightData,
            borderColor: 'orange',
            backgroundColor: 'rgba(255,165,0,0.2)',
            fill: false,
            tension: 0.3
          }

        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'top' },
          title: { display: true, text: 'Last 24h Sensor Data' }
        }
      }
    } as ChartConfiguration);
  }
}
