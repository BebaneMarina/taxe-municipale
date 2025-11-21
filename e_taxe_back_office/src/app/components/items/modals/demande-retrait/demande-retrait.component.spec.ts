import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DemandeRetraitComponent } from './demande-retrait.component';

describe('DemandeRetraitComponent', () => {
  let component: DemandeRetraitComponent;
  let fixture: ComponentFixture<DemandeRetraitComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DemandeRetraitComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DemandeRetraitComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
