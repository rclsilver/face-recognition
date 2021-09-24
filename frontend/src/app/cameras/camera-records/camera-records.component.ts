import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { BehaviorSubject } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { CameraRecord } from 'src/app/models/camera-record.model';
import { Camera } from 'src/app/models/camera.model';
import { ApiService } from 'src/app/services/api.service';

@Component({
  templateUrl: './camera-records.component.html',
  styleUrls: ['./camera-records.component.scss'],
})
export class CameraRecordsComponent implements OnInit {
  private _loading$ = new BehaviorSubject<boolean>(false);
  readonly loading$ = this._loading$.asObservable();

  private _camera$ = new BehaviorSubject<Camera | null>(null);
  readonly camera$ = this._camera$.asObservable();

  private _records$ = new BehaviorSubject<CameraRecord[]>([]);
  readonly records$ = this._records$.asObservable();

  constructor(private _route: ActivatedRoute, private _api: ApiService) {}

  ngOnInit(): void {
    this._route.params.subscribe((params) => {
      this._api
        .getCamera({ id: params.id })
        .pipe(finalize(() => this.refresh()))
        .subscribe((camera) => this._camera$.next(camera));
    });
  }

  refresh(): void {
    if (this._camera$.value) {
      this._loading$.next(true);
      this._api
        .getCameraRecords(this._camera$.value)
        .pipe(finalize(() => this._loading$.next(false)))
        .subscribe(
          (records) => this._records$.next(records),
          () => this._records$.next([])
        );
    }
  }

  delete(record: CameraRecord): void {
    if (this._camera$.value) {
      this._api
        .deleteCameraRecord(this._camera$.value, record.filename)
        .subscribe(() => this.refresh());
    }
  }

  clear(): void {
    if (this._camera$.value) {
      this._api
        .deleteCameraRecords(this._camera$.value)
        .subscribe(() => this.refresh());
    }
  }
}
