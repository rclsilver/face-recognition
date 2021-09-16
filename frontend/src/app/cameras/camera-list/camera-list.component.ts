import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject } from 'rxjs';
import { Camera } from 'src/app/models/camera.model';
import { ApiService } from 'src/app/services/api.service';
import { CameraFormComponent } from '../camera-form/camera-form.component';
import { CameraLiveComponent } from '../camera-live/camera-live.component';

@Component({
  selector: 'app-camera-list',
  templateUrl: './camera-list.component.html',
  styleUrls: ['./camera-list.component.scss'],
})
export class CameraListComponent implements OnInit {
  private _cameras$ = new BehaviorSubject<Camera[]>([]);
  readonly cameras$ = this._cameras$.asObservable();

  private _form$ = new BehaviorSubject<boolean>(false);
  readonly form$ = this._form$.asObservable();

  @ViewChild('form') form?: CameraFormComponent;
  @ViewChild('live') live?: CameraLiveComponent;

  constructor(private _api: ApiService, private _router: Router) {}

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    // Refresh the list
    this._api.getCameras().subscribe((cameras) => this._cameras$.next(cameras));

    // Hide the form
    this._form$.next(false);
  }

  edit(camera?: Camera): void {
    this.form!.camera = camera;
    this._form$.next(true);
  }

  delete(camera: Camera): void {
    this._api.deleteCamera(camera).subscribe(() => this.refresh());
  }

  startLive(camera: Camera): void {
    this.live!.camera = camera;
  }

  displayRecords(camera: Camera): void {
    this._router.navigate([`cameras/${camera.id}`]);
  }
}
