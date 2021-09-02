import {
  Component,
  ElementRef,
  Input,
  OnDestroy,
  ViewChild,
} from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Camera } from 'src/app/models/camera.model';

@Component({
  selector: 'app-camera-live',
  templateUrl: './camera-live.component.html',
  styleUrls: ['./camera-live.component.scss'],
})
export class CameraLiveComponent implements OnDestroy {
  private _show$ = new BehaviorSubject<boolean>(false);
  readonly show$ = this._show$.asObservable();

  @ViewChild('output', { static: true }) output?: ElementRef<HTMLImageElement>;

  @Input() set camera(value: Camera | undefined) {
    if (value) {
      this.output!.nativeElement.src = `/api/streaming/cameras/${value.id}/live`;
      this._show$.next(true);
    } else {
      this.output!.nativeElement.src = '';
      this._show$.next(false);
    }
  }

  ngOnDestroy(): void {
    this.stop();
  }

  stop(): void {
    this.camera = undefined;
  }
}
