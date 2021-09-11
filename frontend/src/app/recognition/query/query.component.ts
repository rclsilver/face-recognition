import { Component, ViewChild } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { finalize, map } from 'rxjs/operators';
import { QueryResult } from 'src/app/models/query-result.model';
import { ApiService } from 'src/app/services/api.service';
import { WebcamComponent } from '../webcam/webcam.component';

export enum QueryMode {
  UPLOAD = 1,
  WEBCAM = 2,
}

@Component({
  templateUrl: './query.component.html',
  styleUrls: ['./query.component.scss'],
})
export class QueryComponent {
  private _result$ = new BehaviorSubject<QueryResult | undefined>(undefined);
  readonly result$ = this._result$.asObservable();

  private _notFound$ = new BehaviorSubject<boolean>(false);
  readonly notFound$ = this._notFound$.asObservable();

  private _progress$ = new BehaviorSubject<boolean>(false);
  readonly progress$ = this._progress$.asObservable();

  private _mode$ = new BehaviorSubject<QueryMode | null>(null);
  readonly mode$ = this._mode$.asObservable();
  readonly webcamMode$ = this.mode$.pipe(
    map((mode) => mode === QueryMode.WEBCAM)
  );
  readonly uploadMode$ = this.mode$.pipe(
    map((mode) => mode === QueryMode.UPLOAD)
  );

  @ViewChild(WebcamComponent) webcam?: WebcamComponent;

  constructor(private _api: ApiService) {}

  setWebcamMode(): void {
    this._mode$.next(QueryMode.WEBCAM);
  }

  setUploadMode(): void {
    this._mode$.next(QueryMode.UPLOAD);
  }

  query(): void {
    if (this._mode$.value == QueryMode.WEBCAM && this.webcam) {
      this.webcam.takeSnapshot();
    }
    if (this._mode$.value == QueryMode.UPLOAD) {
      console.log('on doit upload le fichier');
    }
  }

  reset(): void {
    this._result$.next(undefined);
    this._notFound$.next(false);
    this._progress$.next(false);
  }

  onUpload(event: any): void {
    const file: File = event.target.files[0];

    if (file) {
      this.onCapture(file);
    }
  }

  onCapture(image: Blob): void {
    this._progress$.next(true);
    this._api
      .query(image)
      .pipe(finalize(() => this._progress$.next(false)))
      .subscribe((result) => {
        this._notFound$.next(!result);

        if (result) {
          this._result$.next(result);
        } else {
          this._result$.next(undefined);
        }
      });
  }
}
