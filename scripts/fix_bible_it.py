# current issue in bible_it_toclean.json:
#
# {
#   "Gen": {
#     "title": "Gênesis", // Localized name
#     "chapters": {
#       "1": {
#         "1": "Così dice il Signore, Dio degli eserciti: \"Rècati da questo ministro, presso Sebnà, il maggiordomo, [16b]che si taglia in alto il sepolcro e si scava nella rupe la tomba: [16a]Che cosa possiedi tu qui e chi hai tu qui, che ti stai scavando qui un sepolcro?"
#       } // example verse above, this isn't actually from genesis
#     }
#   },
#   "Exod": { ... }
# }

# problem is the [16b] and [16a] in the verse.
# these exist in multiple verses, and are always in the format [[number][a|b]]
# the goal of this script is to remove these from the verse text.
