/*
 * Sphinx's searchtools.js only defines its default Scorer object if none
 * exists yet (`if (typeof Scorer === "undefined")`), so this file must load
 * before it - see the add_js_file priority in conf.py. Same weights as the
 * Sphinx default, plus a score() hook that down-ranks release/*.rst results:
 * a changelog entry mentioning an API name in passing otherwise scores on
 * equal footing with that API's actual reference page.
 */
var Scorer = {
  objNameMatch: 11,
  objPartialMatch: 6,
  objPrio: {
    0: 15,
    1: 5,
    2: -5,
  },
  objPrioDefault: 0,

  title: 15,
  partialTitle: 7,
  term: 5,
  partialTerm: 2,

  score: result => {
    const [docname, , , , score] = result;
    return docname.startsWith("release/") ? score - 8 : score;
  },
};
