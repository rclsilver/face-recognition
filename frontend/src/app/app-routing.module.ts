import { NgModule } from '@angular/core';
import { ExtraOptions, RouterModule, Routes } from '@angular/router';
import { RequireAdminGuard } from './auth/guards/require-admin.guard';
import { RequireUserGuard } from './auth/guards/require-user.guard';
import { CameraListComponent } from './cameras/camera-list/camera-list.component';
import { IdentityListComponent } from './identities/identity-list/identity-list.component';
import { LearnComponent } from './recognition/learn/learn.component';
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
    ],
  },
  {
    path: 'recognition',
    children: [
      {
        path: 'learn',
        component: LearnComponent,
        canActivate: [RequireAdminGuard],
      },
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
