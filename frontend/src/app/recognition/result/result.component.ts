import {
  Component,
  ElementRef,
  Input,
  OnDestroy,
  ViewChild,
} from '@angular/core';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { Recognition } from 'src/app/models/recognition.model';

export declare class Result {
  image: Blob;
  recognitions: Recognition[];
}

@Component({
  selector: 'app-result',
  templateUrl: './result.component.html',
  styleUrls: ['./result.component.scss'],
})
export class ResultComponent implements OnDestroy {
  readonly width = 640;
  readonly height = 480;

  private _destroyed$ = new Subject<void>();
  private _show$ = new BehaviorSubject<boolean>(false);
  readonly show$ = this._show$.asObservable();

  @ViewChild('canvas', { static: true }) canvas?: ElementRef<HTMLDivElement>;
  @ViewChild('image', { static: true }) image?: ElementRef<HTMLImageElement>;

  constructor() {}

  @Input()
  set result(value: Observable<Result | undefined>) {
    value.pipe(takeUntil(this._destroyed$)).subscribe((result) => {
      if (result) {
        this.draw(result);
      } else {
        this._show$.next(false);
      }
    });
  }

  ngOnDestroy(): void {
    this._destroyed$.next();
    this._destroyed$.complete();
  }

  draw(result: Result): void {
    if (this.image) {
      const reader = new FileReader();

      reader.onloadend = () => {
        // Remove previous canvas
        this.canvas?.nativeElement.childNodes.forEach((child) =>
          this.canvas?.nativeElement.removeChild(child)
        );

        // Create a new canvas
        const canvas = document.createElement('canvas');
        canvas.width = this.width;
        canvas.height = this.height;

        // Load image
        this.image!.nativeElement.src = reader.result as string;

        // Get canvas context and draw rects
        const ctx = canvas.getContext('2d')!;

        // Define styles
        ctx.strokeStyle = 'blue';
        ctx.fillStyle = 'blue';
        ctx.font = '24px serif';
        ctx.textAlign = 'center';

        result.recognitions.forEach((recognition) => {
          ctx.rect(
            recognition.rect.start.x,
            recognition.rect.start.y,
            recognition.rect.end.x - recognition.rect.start.x,
            recognition.rect.end.y - recognition.rect.start.y
          );

          ctx.stroke();

          if (recognition.identity && recognition.score !== null) {
            ctx.fillText(
              `${recognition.identity.first_name} ${recognition.identity.last_name.charAt(0).toUpperCase()}.`,
              recognition.rect.start.x + (recognition.rect.end.x - recognition.rect.start.x) / 2,
              recognition.rect.start.y - 10,
              recognition.rect.end.x - recognition.rect.start.x
            );

            ctx.fillText(
              `${Math.round(recognition.score * 100).toString()} %`,
              recognition.rect.start.x + (recognition.rect.end.x - recognition.rect.start.x) / 2,
              recognition.rect.end.y + 24,
              recognition.rect.end.x - recognition.rect.start.x
            );
          }
        });

        // Display the canvas
        this.canvas!.nativeElement.appendChild(canvas);
        this._show$.next(true);
      };

      reader.readAsDataURL(result.image);
    }
  }
}
