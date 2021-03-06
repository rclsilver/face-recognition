import { NgModule } from '@angular/core';
import { ExtraOptions, RouterModule, Routes } from '@angular/router';
import { RequireAdminGuard } from './auth/guards/require-admin.guard';
import { RequireUserGuard } from './auth/guards/require-user.guard';
import { CameraListComponent } from './cameras/camera-list/camera-list.component';
import { CameraRecordsComponent } from './cameras/camera-records/camera-records.component';
import { IdentityFacesComponent } from './identities/identity-faces/identity-faces.component';
import { IdentityListComponent } from './identities/identity-list/identity-list.component';
import { QueryListComponent } from './queries/query-list/query-list.component';
import { QueryComponent } from './recognition/query/query.component';
import { UserListComponent } from './users/user-list/user-list.component';

const routes: Routes = [
  {
    path: 'users',
    children: [
      {
        path: '',
        component: UserListComponent,
        canActivate: [RequireUserGuard],
      },
    ],
  },
  {
    path: 'identities',
    children: [
      {
        path: '',
        component: IdentityListComponent,
        canActivate: [RequireUserGuard],
      },
      {
        path: ':id',
        component: IdentityFacesComponent,
        canActivate: [RequireAdminGuard],
      },
    ],
  },
  {
    path: 'queries',
    children: [
      {
        path: '',
        component: QueryListComponent,
        canActivate: [RequireAdminGuard],
      },
    ],
  },
  {
    path: 'recognition',
    children: [
      {
        path: 'query',
        component: QueryComponent,
      },
    ],
  },
  {
    path: 'cameras',
    children: [
      {
        path: '',
        component: CameraListComponent,
        canActivate: [RequireUserGuard],
      },
      {
        path: ':id',
        component: CameraRecordsComponent,
        canActivate: [RequireAdminGuard],
      },
    ],
  },
];

const config: ExtraOptions = {
  useHash: true,
  initialNavigation: 'disabled',
};

@NgModule({
  imports: [RouterModule.forRoot(routes, config)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
