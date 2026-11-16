# Weekly plan & Today (current)

```mermaid
flowchart TD
  T[viewToday<br/>:1437] --> S1[schedHtml week strip<br/>:1434 labels DSHORT 'Aero/Anaer']
  T --> W[workout card → tdgo / tdtimer<br/>:2197]
  W --> TR[viewTrain<br/>:1535]
  TR --> S2[weekBar :1471 + strip('train')<br/>:1472 labels DTYPES full]
  TR --> L[listFor :1488 → itemRow :1482 → lastWHtml :1480]
  L --> TM[openTimer :3391 → tick :3353 every 250 ms]
  TR --> ST[stations dayStHtml :1483 → stTick :3734 every 250 ms]
  PT[viewPT :1557] --> S3[strip('pt') :1472 labels FOCI]
```
