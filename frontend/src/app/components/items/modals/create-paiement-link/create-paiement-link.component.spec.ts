import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreatePaiementLinkComponent } from './create-paiement-link.component';

describe('CreatePaiementLinkComponent', () => {
  let component: CreatePaiementLinkComponent;
  let fixture: ComponentFixture<CreatePaiementLinkComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreatePaiementLinkComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreatePaiementLinkComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
