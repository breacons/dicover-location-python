import { map } from 'rxjs/operators';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import * as io from 'socket.io-client';
import { Observable } from 'rxjs';
import {
  UserUpdate,
  LocationUpdate,
  LeaderboardEntry,
  TeamLeaderboardEntry
} from './location-update.model';

@Injectable({
  providedIn: 'root'
})
export class LocationUpdatesService {
  private url = 'http://localhost:5000';
  private socket;

  constructor(private http: HttpClient) {
    this.socket = io(this.url);
    console.log('Created...');
  }

  public getUpdates = () => {
    return new Observable(observer => {
      this.socket.on('connect', () => {
        console.log('Connected');
        this.socket.on('FromAPI', message => {
          const update = message.data || {};
          const locationUpdate = new LocationUpdate();
          if (!!update) {
            if (update.positions) {
              Object.keys(update.positions).map(key => {
                const userUpdate = new UserUpdate();
                userUpdate.id = key;
                userUpdate.latitude = update.positions[key].latitude;
                userUpdate.longitude = update.positions[key].longitude;
                userUpdate.score = update.positions[key].score;
                userUpdate.team = update.positions[key].team;
                locationUpdate.users.push(userUpdate);
              });
            }
            if (update.leaderboard) {
              Object.keys(update.leaderboard).map(key => {
                const leaderboardEntry = new LeaderboardEntry();
                leaderboardEntry.id = key;
                leaderboardEntry.score = update.leaderboard[key];
                locationUpdate.leaderboard.push(leaderboardEntry);
              });
              locationUpdate.leaderboard = locationUpdate.leaderboard.sort(
                (a, b) => b.score - a.score
              );
            }
            if (update.teams) {
              Object.keys(update.teams).map(key => {
                const teamLeaderboardEntry = new TeamLeaderboardEntry();
                teamLeaderboardEntry.teamId = key;
                teamLeaderboardEntry.score = update.teams[key];
                locationUpdate.teamLeaderboard.push(teamLeaderboardEntry);
              });
              locationUpdate.teamLeaderboard = locationUpdate.teamLeaderboard.sort(
                (a, b) => b.score - a.score
              );
            }
            locationUpdate.time = new Date(update.time);
            observer.next(locationUpdate);
          }
        });
      });
    });
  };

  startServer() {
    return this.http.get('http://localhost:5000/load');
  }
}
