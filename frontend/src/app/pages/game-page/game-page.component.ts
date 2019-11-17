import { LocationScatterChartComponent } from './../../charts/location-scatter-chart/location-scatter-chart.component';
import {
  LocationUpdate,
  LeaderboardEntry,
  TeamLeaderboardEntry
} from './../../services/location-update.model';
import { LocationUpdatesService } from './../../services/location-updates.service';
import { Component, OnInit, ViewChild } from '@angular/core';
import { take, debounceTime, auditTime } from 'rxjs/operators';

@Component({
  selector: 'app-game-page',
  templateUrl: './game-page.component.html',
  styleUrls: ['./game-page.component.scss']
})
export class GamePageComponent implements OnInit {
  @ViewChild(LocationScatterChartComponent, { static: true })
  scatterChart: LocationScatterChartComponent;
  initalized: boolean;
  leaderBoard: LeaderboardEntry[] = [];
  teamLeaderBoard: TeamLeaderboardEntry[] = [];
  timestamp = null;
  status = 'Connecting to server...';
  constructor(private updatesService: LocationUpdatesService) {}

  ngOnInit() {
    this.startServer();
  }

  async startServer() {
    this.status = 'Connecting to server...';
    this.updatesService
      .startServer()
      .pipe(take(1))
      .toPromise();
    this.updatesService
      .getUpdates()
      .pipe(auditTime(200))
      .subscribe((message: LocationUpdate) => {
        this.status = 'Receiving events...';
        // console.log('Top teams: ', message.teamLeaderboard);
        if (!this.initalized) {
          this.initChart(message as LocationUpdate);
        } else {
          this.updateChart(message as LocationUpdate);
        }
        if (message.leaderboard.length) {
          this.leaderBoard = message.leaderboard;
        }
        if (message.teamLeaderboard.length) {
          const total = message.teamLeaderboard
            .map(entry => entry.score)
            .reduce((prev, next) => prev + next, 0);
          message.teamLeaderboard.forEach(entry => {
            entry.score = Math.floor((entry.score / total) * 100);
          });
          this.teamLeaderBoard = message.teamLeaderboard;
          this.timestamp = message.time;
        }
      });
  }

  trackLeaderBoardItems(index, item){
    return item ? item.teamId : null;
  }

  private initChart(locationUpdate: LocationUpdate) {
    this.scatterChart.setChartData(this.convertToChart(locationUpdate));
    this.initalized = true;
  }

  private updateChart(locationUpdate: LocationUpdate) {
    const lookup = this.convertToLookupTable(locationUpdate);
    this.scatterChart.updateData(lookup);
  }

  private convertToLookupTable(locationUpdate: LocationUpdate) {
    const lookupTable = {};
    locationUpdate.users.forEach(userUpdate => {
      lookupTable[userUpdate.id] = {
        x: userUpdate.latitude,
        y: userUpdate.longitude,
        id: userUpdate.id,
        team: userUpdate.team,
        r: (userUpdate.score / 10) < 1 ? 5 : (userUpdate.score / 15) + 5
      };
    });
    // console.log(lookupTable);
    return lookupTable;
  }
  private convertToChart(locationUpdate: LocationUpdate) {
    const chartUpdate = locationUpdate.users.map(userUpdate => {
      console.log(userUpdate.team);
      return {
        data: [
          {
            x: userUpdate.latitude,
            y: userUpdate.longitude,
            id: userUpdate.id,
            r: (userUpdate.score / 10) < 1 ? 5 : (userUpdate.score / 15) + 5
          }
        ],
        borderColor: '#' + userUpdate.team,
        backgroundColor: '#' + userUpdate.team,
        fill: true,
        teamId: userUpdate.team
      };
    });
    return chartUpdate;
  }
}
