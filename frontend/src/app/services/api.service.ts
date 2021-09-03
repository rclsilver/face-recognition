import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Camera } from '../models/camera.model';
import { FaceEncoding } from '../models/face-encoding.model';
import { Identity } from '../models/identity.model';
import { Recognition } from '../models/recognition.model';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  constructor(private _http: HttpClient) {}

  getIdentities(): Observable<Identity[]> {
    return this._http.get<Identity[]>('/api/identities/');
  }

  createIdentity(
    payload: Pick<Identity, 'first_name' | 'last_name'>
  ): Observable<Identity> {
    return this._http.post<Identity>('/api/identities/', payload);
  }

  updateIdentity(
    identity: Pick<Identity, 'id'>,
    payload: Pick<Identity, 'first_name' | 'last_name'>
  ): Observable<Identity> {
    return this._http.put<Identity>(`/api/identities/${identity.id}`, payload);
  }

  deleteIdentity(identity: Pick<Identity, 'id'>): Observable<void> {
    return this._http.delete<void>(`/api/identities/${identity.id}`);
  }

  getCameras(): Observable<Camera[]> {
    return this._http.get<Camera[]>('/api/cameras/');
  }

  createCamera(payload: Pick<Camera, 'label' | 'url'>): Observable<Camera> {
    return this._http.post<Camera>('/api/cameras/', payload);
  }

  updateCamera(
    camera: Pick<Camera, 'id'>,
    payload: Pick<Camera, 'label' | 'url'>
  ): Observable<Camera> {
    return this._http.put<Camera>(`/api/cameras/${camera.id}`, payload);
  }

  deleteCamera(camera: Pick<Camera, 'id'>): Observable<void> {
    return this._http.delete<void>(`/api/cameras/${camera.id}`);
  }

  query(image: Blob): Observable<Recognition[] | null> {
    const payload = new FormData();
    payload.append('picture', image, 'webcam.jpg');

    return this._http.post<Recognition[] | null>(
      '/api/recognition/query',
      payload
    );
  }

  learn(identity: Pick<Identity, 'id'>, image: Blob): Observable<FaceEncoding> {
    const payload = new FormData();
    payload.append('picture', image, 'webcam.jpg');

    return this._http.post<FaceEncoding>(
      `/api/identities/${identity.id}/learn`,
      payload
    );
  }
}
