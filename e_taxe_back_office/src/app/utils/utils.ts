import {ActivatedRoute} from '@angular/router';

export function getGradient(ctx : any, chartArea : any) {
  let width, height, gradient;
  const chartWidth = chartArea.right - chartArea.left;
  const chartHeight = chartArea.bottom - chartArea.top;
  if (!gradient || width !== chartWidth || height !== chartHeight) {
    // Create the gradient because this is either the first render
    // or the size of the chart has changed
    width = chartWidth;
    height = chartHeight;
    gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
    gradient.addColorStop(0, "#fff");
    gradient.addColorStop(0, "#fff");
    gradient.addColorStop(0.5, "rgba(12, 82, 156, 1)");
    gradient.addColorStop(0.5, "rgba(12, 82, 156, 1)");
  }

  return gradient;
}
export function dateFormater(date: string,separator : string = '-'): string
{
  const d = new Date(date);
  return `${d.getDate()}${separator}${d.getMonth() + 1}${separator}${d.getFullYear()} ${d.getHours() < 10 ? '0' + d.getHours() : d.getHours()}:${d.getMinutes() < 10 ? '0' + d.getMinutes() : d.getMinutes()}`;
}

export function parseMount(mount: string,separator : string): string
{
  const arrayMount : string[] = mount.split('.');
  const parseMount : number = parseInt(arrayMount[0]);
  return `${parseMount.toLocaleString()}${separator}${arrayMount[1]}`;
}

export function cutString(value: string, size : number = 7): string
{
  let arrayValue: string[] = value.split('');
  if (arrayValue.length > size) {
    arrayValue.length = size;
    return  arrayValue.join('') + '...';
  }
  return  arrayValue.join('');
}

export function hiddenLetters(text : string,display : number = 4): string
{
  if (text.length <= display) return  text;

  let cutString : string[] = new Array(Math.floor(text.length/display - 1)).fill(new Array(display).fill("*").join(""));
  let rest : string[] = new Array(1).fill(new Array(text.length % display).fill("*").join(""));

  return rest.join(' ') + ' ' + cutString.join(' ') + ' ' + text.split('').slice(-display).join('');
}
