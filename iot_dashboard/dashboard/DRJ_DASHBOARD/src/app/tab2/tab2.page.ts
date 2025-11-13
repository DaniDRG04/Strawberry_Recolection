import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

import { IonContent, IonHeader, IonToolbar, IonGrid, IonIcon, IonRow, IonButton, IonDatetime, IonTitle, IonCol, IonCard, IonCardSubtitle, IonCardHeader, IonCardTitle, IonCardContent } from '@ionic/angular/standalone';
import { Chart, registerables } from 'chart.js';
import { addIcons } from 'ionicons';
import { chevronBackOutline, chevronForwardOutline } from 'ionicons/icons';

Chart.register(...registerables);

@Component({
  selector: 'app-tab2',
  templateUrl: 'tab2.page.html',
  styleUrls: ['tab2.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    HttpClientModule,
    IonHeader,
    IonToolbar,
    IonIcon,
    IonTitle,
    IonContent,
    IonButton,
    IonDatetime,
    IonGrid,
    IonRow,
    IonCol,
    IonCard,
    IonCardSubtitle,
    IonCardHeader,
    IonCardTitle,
    IonCardContent
  ]
})
export class Tab2Page implements OnInit, OnDestroy {
  chart: Chart | null = null;

  startDate: string | null = null;
  endDate: string | null = null;

  images: { timestamp: string, url: string }[] = [];
  displayedImages: { timestamp: string, url: string }[] = [];
  currentPage = 0;
  pageSize = 10;

  sensorData: { timestamp: string, temperatureData: number, humidityData: number, soilData: number, lightData: number }[] = [];

  constructor(private http: HttpClient) {
    addIcons({
      'chevron-back-outline': chevronBackOutline,
      'chevron-forward-outline': chevronForwardOutline,
    });
  }

  ngOnInit() {
    this.loadAllData();
  }

  ionViewWillLeave() {
    this.destroyChart();
  }

  ngOnDestroy() {
    this.destroyChart();
  }

  destroyChart() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
  }

  formatTimestamp(ts: string): string {
  const d = new Date(ts);
  return d.toLocaleString(); // shows local date + time
}


  // ---------------------------
  // Fetch all data from Flask
  // ---------------------------
// ---------------------------
// Fetch all data from Flask
// ---------------------------
loadAllData() {
  this.http.get<any>('http://10.25.15.228:5000/alldata').subscribe(res => {
    // Sensor data
    this.sensorData = res.sensorData.map((row: any) => ({
      timestamp: row.date_time,
      temperatureData: row.temp_air,
      humidityData: row.hum_air,
      soilData: row.hum_soil,
      lightData: row.light
    }));

    // Images
    this.images = res.images.map((img: any) => ({
      timestamp: img.date_time,
      url: `data:image/png;base64,${img.image_base64}`
    }));

    // Initially display first page of images
    this.updateDisplayedImages();

    // Initially draw chart with all sensor data
    this.updateChart();
  });
}

// ---------------------------
// Apply filter based on selected dates
// ---------------------------
applyDateFilter() {
  if (!this.startDate || !this.endDate) return;

  const start = new Date(this.startDate);
  const end = new Date(this.endDate);
  end.setHours(23, 59, 59, 999); // include full end day

  // Filter sensor data
  const filteredSensor = this.sensorData.filter(d => {
    const ts = new Date(d.timestamp);
    return ts >= start && ts <= end;
  });

  const labels = filteredSensor.map(d => new Date(d.timestamp).toLocaleString());
  const tempData = filteredSensor.map(d => d.temperatureData);
  const humData = filteredSensor.map(d => d.humidityData);
  const soilData = filteredSensor.map(d => d.soilData);
  const lightData = filteredSensor.map(d => d.lightData);

  // Update chart
  this.updateChart(labels, tempData, humData, soilData, lightData);

  // Filter images
  const filteredImages = this.images.filter(img => {
    const ts = new Date(img.timestamp);
    return ts >= start && ts <= end;
  });

  this.displayedImages = filteredImages.slice(0, this.pageSize);
  this.currentPage = 0;
}

  // ---------------------------
  // Update Chart
  // ---------------------------
  updateChart(labels?: string[], tempData?: number[], humData?: number[], soilData?: number[], lightData?: number[]) {
    const ctx = document.getElementById('sensorChart') as HTMLCanvasElement;
    if (!ctx) return;

    if (this.chart) this.chart.destroy();

    this.chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels || this.sensorData.map(d => new Date(d.timestamp).toLocaleString()),
        datasets: [
          { label: 'Temperature (°C)', data: tempData || this.sensorData.map(d => d.temperatureData), borderColor: 'red', fill: false },
          { label: 'Humidity (%)', data: humData || this.sensorData.map(d => d.humidityData), borderColor: 'blue', fill: false },
          { label: 'Soil Moisture (%)', data: soilData || this.sensorData.map(d => d.soilData), borderColor: 'green', fill: false },
          { label: 'Light Intensity (%)', data: lightData || this.sensorData.map(d => d.lightData), borderColor: 'orange', fill: false }
        ]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }

  // ---------------------------
  // Pagination for images
  // ---------------------------
  updateDisplayedImages() {
    const startIndex = this.currentPage * this.pageSize;
    const endIndex = startIndex + this.pageSize;
    this.displayedImages = this.images.slice(startIndex, endIndex);
  }

  prevPage() {
    if (this.currentPage > 0) {
      this.currentPage--;
      this.updateDisplayedImages();
    }
  }

  nextPage() {
    if ((this.currentPage + 1) * this.pageSize < this.images.length) {
      this.currentPage++;
      this.updateDisplayedImages();
    }
  }
}
