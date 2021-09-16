import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CameraRecordsComponent } from './camera-records.component';

describe('CameraRecordsComponent', () => {
  let component: CameraRecordsComponent;
  let fixture: ComponentFixture<CameraRecordsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CameraRecordsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CameraRecordsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
