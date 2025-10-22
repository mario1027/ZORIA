from dash import html
from dash_svg import Svg, Path

class ICON:
    class CIRCUIT:
        RESISTOR = Svg([
            Path(d='M2 10h2l2-2h2l2 2h2l2-2h2l2 2h2v2h-2l-2 2h-2l-2-2h-2l-2 2H2v-2z')
        ], className='icon icon-sm me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

        CAPACITOR = Svg([
            Path(d='M4 10h4v4H4v-4zm8 0h4v4h-4v-4z')
        ], className='icon icon-sm me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

        INDUCTOR = Svg([
            Path(d='M4 10c0-1.1.9-2 2-2s2 .9 2 2-.9 2-2 2-2-.9-2-2zm8 0c0-1.1.9-2 2-2s2 .9 2 2-.9 2-2 2-2-.9-2-2z')
        ], className='icon icon-sm me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

        RLC_SERIES = Svg([
            Path(d='M2 10h2l2-2h2l2 2h2l2-2h2l2 2h2v2h-2l-2 2h-2l-2-2h-2l-2 2H2v-2z')
        ], className='icon icon-sm me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

        RLC_PARALLEL = Svg([
            Path(d='M4 8h4v8H4V8zm8 0h4v8h-4V8z')
        ], className='icon icon-sm me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

    class MEASUREMENT:
        IMPEDANCE = Svg([
            Path(d='M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z')
        ], className='icon icon-sm me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

        FREQUENCY = Svg([
            Path(d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z')
        ], className='icon icon-sm me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

        PHASE = Svg([
            Path(d='M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z')
        ], className='icon icon-sm me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

    class CALCULATION:
        CALCULATOR = Svg([
            Path(d='M7 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2h-2V0h-2v2H9V0H7v2zM5 6h14v2H5V6zm0 4h14v2H5v-2zm0 4h14v2H5v-2z')
        ], className='icon icon-sm me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

        GRAPH = Svg([
            Path(d='M3 3v18h18V3H3zm16 16H5V5h14v14zM7 9h2v6H7V9zm4-2h2v8h-2V7zm4 3h2v5h-2v-5z')
        ], className='icon icon-sm me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

    class SETTINGS:
        GEAR = Svg([
            Path(d='M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.82,11.69,4.82,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.43-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z')
        ], className='icon icon-sm me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

    class STATUS:
        SUCCESS = Svg([
            Path(d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z')
        ], className='icon icon-sm text-success me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

        ERROR = Svg([
            Path(d='M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm5 13.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12 17 15.59z')
        ], className='icon icon-sm text-danger me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

        WARNING = Svg([
            Path(d='M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z')
        ], className='icon icon-sm text-warning me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

    class ACTION:
        PLAY = Svg([
            Path(d='M8 5v14l11-7z')
        ], className='icon icon-sm me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

        PAUSE = Svg([
            Path(d='M6 19h4V5H6v14zm8-14v14h4V5h-4z')
        ], className='icon icon-sm me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

        STOP = Svg([
            Path(d='M6 6h12v12H6z')
        ], className='icon icon-sm me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')

        RESET = Svg([
            Path(d='M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z')
        ], className='icon icon-sm me-2', fill='currentColor', viewBox='0 0 24 24', xmlns='http://www.w3.org/2000/svg')