import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';

import { WebcamModule } from 'ngx-webcam';
import { HttpClientModule } from '@angular/common/http';
import { TopMenuComponent } from './page/top-menu/top-menu.component';
import { IdentityListComponent } from './identities/identity-list/identity-list.component';
import { QueryComponent } from './recognition/query/query.component';
import { WebcamComponent } from './recognition/webcam/webcam.component';
import { IdentityFormComponent } from './identities/identity-form/identity-form.component';
import { FormsModule } from '@angular/forms';
import { CameraListComponent } from './cameras/camera-list/camera-list.component';
import { CameraFormComponent } from './cameras/camera-form/camera-form.component';
import { CameraLiveComponent } from './cameras/camera-live/camera-live.component';
import { UserListComponent } from './users/user-list/user-list.component';
import { AuthModule } from './auth/auth.module';
import { UserMenuComponent } from './page/user-menu/user-menu.component';
import { QueryListComponent } from './queries/query-list/query-list.component';
import { IdentityFacesComponent } from './identities/identity-faces/identity-faces.component';
import { CameraRecordsComponent } from './cameras/camera-records/camera-records.component';

@NgModule({
  declarations: [
    AppComponent,
    TopMenuComponent,
    IdentityListComponent,
    QueryComponent,
    WebcamComponent,
    IdentityFormComponent,
    CameraListComponent,
    CameraFormComponent,
    CameraLiveComponent,
    UserListComponent,
    UserMenuComponent,
    QueryListComponent,
    IdentityFacesComponent,
    CameraRecordsComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    WebcamModule,
    AuthModule.forRoot(),
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
