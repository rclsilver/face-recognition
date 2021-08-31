import { Component, EventEmitter, Output } from '@angular/core';
import { WebcamImage } from 'ngx-webcam';
import { Subject } from 'rxjs';

@Component({
  selector: 'app-webcam',
  templateUrl: './webcam.component.html',
  styleUrls: ['./webcam.component.scss'],
})
export class WebcamComponent {
  // Webcam settings
  readonly imageType = 'image/jpeg';
  readonly imageQuality = 1;

  // Capture trigger
  private _trigger$ = new Subject<void>();
  readonly trigger$ = this._trigger$.asObservable();

  // Capture event
  @Output() snapshot = new EventEmitter<Blob>();

  constructor() {}

  capture(image: WebcamImage): void {
    const bytesString = atob(image.imageAsBase64);
    const bytes = new Uint8Array(bytesString.length);

    for (let i = 0; i < bytesString.length; ++i) {
      bytes[i] = bytesString.charCodeAt(i);
    }

    const file = new Blob([bytes], {
      type: this.imageType,
    });

    this.snapshot.emit(file);
  }

  takeSnapshot(): void {
    this._trigger$.next();
  }
}
