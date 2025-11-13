import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { 
  IonContent, IonHeader, IonToolbar, IonTitle, IonGrid, IonRow, IonCol,
  IonCard, IonCardHeader, IonCardTitle, IonCardSubtitle, IonCardContent,
  IonButton, IonDatetime, IonItem, IonLabel, IonText
} from '@ionic/angular/standalone';

@Component({
  selector: 'app-tab3',
  templateUrl: 'tab3.page.html',
  styleUrls: ['tab3.page.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    HttpClientModule,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonContent,
    IonGrid,
    IonRow,
    IonCol,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardSubtitle,
    IonCardContent,
    IonButton,
    IonDatetime,
    IonItem,
    IonLabel,
    IonText
  ],
})
export class Tab3Page {
  startDate: string | null = null;
  endDate: string | null = null;

  errorData: { date_time: string, error: string }[] = [];
  filteredErrors: { date_time: string, error: string }[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadAllData();
  }

  // ---- Safe MySQL → Date parser ----
  parseMySQLDate(mysqlDate: string): Date {
    return new Date(mysqlDate.replace(' ', 'T'));
  }

  formatTimestamp(ts: string): string {
    const d = this.parseMySQLDate(ts);
    return isNaN(d.getTime()) ? ts : d.toLocaleString();
  }

  // ---- Fetch all data ----
  loadAllData() {
    this.http.get<any>('http://10.25.15.228:5000/alldata').subscribe(res => {
      this.errorData = (res.errors || []).map((e: any) => ({
        date_time: e.date_time,
        error: e.error
      }));

      // Sort descending
      this.errorData.sort(
        (a, b) => this.parseMySQLDate(b.date_time).getTime() - this.parseMySQLDate(a.date_time).getTime()
      );

      // Show all initially
      this.filteredErrors = [...this.errorData];
      console.log('Loaded error data:', this.errorData);
    });
  }

  // ---- Filtering ----
  filterByDate() {
    if (!this.startDate && !this.endDate) {
      this.filteredErrors = [...this.errorData];
      return;
    }

    const start = this.startDate ? new Date(this.startDate).getTime() : 0;
    const end = this.endDate ? new Date(this.endDate).getTime() : Date.now();

    this.filteredErrors = this.errorData.filter(e => {
      const ts = this.parseMySQLDate(e.date_time).getTime();
      return ts >= start && ts <= end;
    });

    console.log('Filtered errors:', this.filteredErrors);
  }

  clearFilter() {
    this.startDate = null;
    this.endDate = null;
    this.filteredErrors = [...this.errorData];
  }
}
