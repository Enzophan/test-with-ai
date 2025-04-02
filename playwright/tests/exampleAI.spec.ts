import { expect } from "@playwright/test";
import { test } from "./fixture";
 
test.beforeEach(async ({ page }) => {
  page.setViewportSize({ width: 1280, height: 760 });
  await page.goto("https://www.bbc.com/sport");
});
 
test("find and output all premier league matches", async ({
  ai,
  aiQuery,
}) => {
  await ai('click the football tab which is next to "Home"');
 
  await ai('click "Scores & Fixtures" which is under the sports tabs');
 
  await ai('scroll the page until all "Premier League" games are in view underneath the "Premier League" heading, stop when another group or league is visible');
 
  const matches = await aiQuery(
    "string[], find all 'Premier League' matches on the page and the scores, output them in the match format"
  );
 
  console.log("these are the team names and scores", matches);
  expect(matches?.length).toBeGreaterThan(0);
});