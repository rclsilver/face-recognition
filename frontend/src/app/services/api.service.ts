import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { CameraRecord } from '../models/camera-record.model';
import { Camera } from '../models/camera.model';
import { FaceEncoding } from '../models/face-encoding.model';
import { Identity } from '../models/identity.model';
import { QueryResult } from '../models/query-result.model';
import { Query } from '../models/query.model';
import { Recognition } from '../models/recognition.model';
import { Suggestion } from '../models/suggestion.model';
import { User } from '../models/user.model';

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

  clearIdentity(identity: Pick<Identity, 'id'>): Observable<void> {
    return this._http.post<void>(`/api/identities/${identity.id}/clear`, {});
  }

  getIdentity(identity: Pick<Identity, 'id'>): Observable<Identity> {
    return this._http.get<Identity>(`/api/identities/${identity.id}`);
  }

  getIdentityFaces(identity: Pick<Identity, 'id'>): Observable<FaceEncoding[]> {
    return this._http.get<FaceEncoding[]>(
      `/api/identities/${identity.id}/faces`
    );
  }

  deleteIdentityFace(
    identity: Pick<Identity, 'id'>,
    face: Pick<FaceEncoding, 'id'>
  ): Observable<void> {
    return this._http.delete<void>(
      `/api/identities/${identity.id}/faces/${face.id}`
    );
  }

  getUsers(): Observable<User[]> {
    return this._http.get<User[]>('/api/users/');
  }

  getUser(user: Pick<User, 'id'>): Observable<Identity> {
    return this._http.get<Identity>(`/api/identities/${user.id}`);
  }

  deleteUser(user: Pick<User, 'id'>): Observable<void> {
    return this._http.delete<void>(`/api/users/${user.id}`);
  }

  getCameras(): Observable<Camera[]> {
    return this._http.get<Camera[]>('/api/cameras/');
  }

  getCamera(camera: Pick<Camera, 'id'>): Observable<Camera> {
    return this._http.get<Camera>(`/api/cameras/${camera.id}`);
  }

  getCameraRecords(camera: Pick<Camera, 'id'>): Observable<CameraRecord[]> {
    return this._http.get<CameraRecord[]>(`/api/cameras/${camera.id}/records`);
  }

  deleteCameraRecord(
    camera: Pick<Camera, 'id'>,
    recordName: string
  ): Observable<void> {
    return this._http.delete<void>(
      `/api/cameras/${camera.id}/records/${recordName}`
    );
  }

  deleteCameraRecords(camera: Pick<Camera, 'id'>): Observable<void> {
    return this._http.delete<void>(`/api/cameras/${camera.id}/records`);
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

  query(image: Blob): Observable<QueryResult | null> {
    const payload = new FormData();
    payload.append('picture', image, 'webcam.jpg');

    return this._http.post<QueryResult | null>(
      '/api/recognition/query?returns=1',
      payload
    );
  }

  getQueries(): Observable<Query[]> {
    return this._http.get<Query[]>('/api/recognition/queries');
  }

  confirmSuggestion(
    query: Query,
    suggestion: Suggestion
  ): Observable<Recognition> {
    return this._http.post<Recognition>(
      `/api/recognition/queries/${query.id}/${suggestion.id}`,
      {
        identity: suggestion.identity,
      }
    );
  }

  deleteSuggestion(query: Query, suggestion: Suggestion): Observable<void> {
    return this._http.delete<void>(
      `/api/recognition/queries/${query.id}/${suggestion.id}`
    );
  }

  clearSuggestions(): Observable<void> {
    return this._http.delete<void>('/api/recognition/queries/');
  }
}
