import {
  AfterViewInit,
  Component,
  ElementRef,
  Input,
  OnDestroy,
  ViewChild,
} from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { AuthService } from 'src/app/auth/auth.service';
import { Camera } from 'src/app/models/camera.model';

@Component({
  selector: 'app-camera-live',
  templateUrl: './camera-live.component.html',
  styleUrls: ['./camera-live.component.scss'],
})
export class CameraLiveComponent implements AfterViewInit, OnDestroy {
  private _show$ = new BehaviorSubject<boolean>(false);
  private _error$ = new BehaviorSubject<boolean>(false);
  private _loading$ = new BehaviorSubject<boolean>(false);

  readonly show$ = this._show$.asObservable();
  readonly error$ = this._error$.asObservable();
  readonly loading$ = this._loading$.asObservable();

  @ViewChild('output', { static: true }) output?: ElementRef<HTMLImageElement>;

  @Input() set camera(value: Camera | undefined) {
    if (value) {
      this._show();
      this._loading();
      this.output!.nativeElement.src = `/api/cameras/${value.id}/live?token=${this._auth.accessToken}`;
    } else {
      this.output!.nativeElement.src = '';
      this._hide();
    }
  }

  constructor(private _auth: AuthService) {}

  ngAfterViewInit(): void {
    this.output!.nativeElement.onload = () => {
      this._ready();
    };

    this.output!.nativeElement.onerror = () => {
      this.output!.nativeElement.src = '';
      this._error();
    };
  }

  ngOnDestroy(): void {
    this.stop();
  }

  private _loading(): void {
    this._error$.next(false);
    this._loading$.next(true);
  }

  private _ready(): void {
    this._error$.next(false);
    this._loading$.next(false);
  }

  private _error(): void {
    this._loading$.next(false);
    this._error$.next(true);
  }

  private _show(): void {
    this._show$.next(true);
  }

  private _hide(): void {
    this._show$.next(false);
  }

  stop(): void {
    this.camera = undefined;
  }
}
