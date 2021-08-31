import { Component, ViewChild } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Recognition } from 'src/app/models/recognition.model';
import { ApiService } from 'src/app/services/api.service';
import { Result } from '../result/result.component';
import { WebcamComponent } from '../webcam/webcam.component';

@Component({
  templateUrl: './query.component.html',
  styleUrls: ['./query.component.scss'],
})
export class QueryComponent {
  private _result$ = new BehaviorSubject<Result | undefined>(undefined);
  readonly result$ = this._result$.asObservable();

  private _notFound$ = new BehaviorSubject<boolean>(false);
  readonly notFound$ = this._notFound$.asObservable();

  @ViewChild(WebcamComponent) webcam?: WebcamComponent;

  constructor(private _api: ApiService) {}

  query(): void {
    if (this.webcam) {
      this.webcam.takeSnapshot();
    }
  }

  reset(): void {
    this._result$.next(undefined);
    this._notFound$.next(false);
  }

  onCapture(image: Blob): void {
    this._api.query(image).subscribe((result) => {
      this._notFound$.next(!result);

      if (result) {
        this._result$.next({
          image,
          recognitions: result,
        });
      } else {
        this._result$.next(undefined);
      }
    });
  }
}
