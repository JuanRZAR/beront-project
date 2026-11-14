export function wrapDistance(index: number, current: number, count: number) {
  const distance = (((index - current) % count) + count) % count;
  return distance > count / 2 ? distance - count : distance;
}
export function itemPlacement(distance: number, gap: number) {
  const steps = Math.abs(distance);
  return {
    transform: `translateX(${distance * gap}px) scale(${steps === 0 ? 1 : 0.9})`,
    visible: steps <= 2,
    layer: 10 - steps,
  };
}
