import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Camera } from 'src/app/models/camera.model';
import { Identity } from 'src/app/models/identity.model';
import { ApiService } from 'src/app/services/api.service';

@Component({
  selector: 'app-camera-form',
  templateUrl: './camera-form.component.html',
  styleUrls: ['./camera-form.component.scss'],
})
export class CameraFormComponent {
  private _current?: Camera;

  @Input() set camera(value: Camera | undefined) {
    this._current = value;

    if (value) {
      this.record.label = value.label;
      this.record.url = value.url;
    } else {
      this.record.label = '';
      this.record.url = '';
    }
  }

  @Output() submit = new EventEmitter<Camera>();

  record: Pick<Camera, 'label' | 'url'> = {
    label: '',
    url: '',
  };

  constructor(private _api: ApiService) {}

  submitForm(): void {
    const request = this._current
      ? this._api.updateCamera(this._current, this.record)
      : this._api.createCamera(this.record);

    request.subscribe(
      (result) => {
        this.submit.emit(result);
      },
      (error) => {
        console.error(error);
      }
    );
  }
}
