import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { WebcamImage } from 'ngx-webcam';
import { BehaviorSubject, Subject } from 'rxjs';

@Component({
  selector: 'app-test-webcam',
  templateUrl: './test-webcam.component.html',
  styleUrls: ['./test-webcam.component.scss'],
})
export class TestWebcamComponent {
  private _trigger$ = new Subject<void>();
  private _result$ = new BehaviorSubject<
    { name: string; score: number }[] | undefined
  >(undefined);

  readonly trigger$ = this._trigger$.asObservable();
  readonly result$ = this._result$.asObservable();
  readonly imageType = 'image/png';
  readonly imageQuality = 1;

  constructor(private _http: HttpClient) {}

  capture(): void {
    this._trigger$.next();
  }

  _learn(image: WebcamImage): void {
    const bytesString = atob(image.imageAsBase64);
    const bytes = new Uint8Array(bytesString.length);

    for (let i = 0; i < bytesString.length; ++i) {
      bytes[i] = bytesString.charCodeAt(i);
    }

    const file = new Blob([bytes], {
      type: this.imageType,
    });

    const payload = new FormData();
    payload.append('picture', file, 'webcam.png');

    this._http
      .post<{ identity: any }[] | null>(
        '/api/identities/d96a8b1c-b4af-4fc5-b294-45f5c8562e86/learn',
        payload
      )
      .subscribe((result) => {
        if (result) {
          this._result$.next(
            result.map((v) => {
              return {
                name: `${v.identity.first_name} ${v.identity.last_name}`,
                score: 100,
              };
            })
          );
        } else {
          this._result$.next(undefined);
        }
      });
  }

  _query(image: WebcamImage): void {
    const bytesString = atob(image.imageAsBase64);
    const bytes = new Uint8Array(bytesString.length);

    for (let i = 0; i < bytesString.length; ++i) {
      bytes[i] = bytesString.charCodeAt(i);
    }

    const file = new Blob([bytes], {
      type: this.imageType,
    });

    const payload = new FormData();
    payload.append('picture', file, 'webcam.png');

    this._http
      .post<{ identity: any; score: number }[] | null>(
        '/api/recognition/query',
        payload
      )
      .subscribe((result) => {
        if (result) {
          this._result$.next(
            result.map((v) => {
              return {
                name: `${v.identity.first_name} ${v.identity.last_name}`,
                score: Math.round(v.score * 100),
              };
            })
          );
        } else {
          this._result$.next(undefined);
        }
      });
  }

  identify(image: WebcamImage): void {
    //this._learn(image);
    this._query(image);
  }
}
