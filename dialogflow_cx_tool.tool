name:xu-kanjian-Machine-Learning-Model-Music-Recommendations
type:OpenAPI

Schema:

openapi: 3.0.0
info:
  title: Music Recommendation API
  version: v1
servers:
  - url: https://us-central1-baidao-training-2023.cloudfunctions.net/xu-kanjian-music-recommendation-system
paths:
  /:
    post:
      summary: Get music recommendations based on a list of favorite songs.
      operationId: getMusicRecommendations
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                songs:
                  type: array
                  description: A list of favorite songs.
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                        description: The name of the song.
                      year:
                        type: integer
                        description: The year the song was released.
              example:
                songs:
                  - name: "Come As You Are"
                    year: 1991
                  - name: "Smells Like Teen Spirit"
                    year: 1991
      responses:
        '200':
          description: A list of recommended songs.
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    name:
                      type: string
                      description: The name of the recommended song.
                    year:
                      type: integer
                      description: The year the recommended song was released.
                    artists:
                      type: string
                      description: The artists of the recommended song.
              example:
                - name: "Song Title 1"
                  year: 2023
                  artists: "Artist 1"
                - name: "Song Title 2"
                  year: 2022
                  artists: "Artist 2"
        '400':
          description: Bad Request - Missing 'songs' key in request body.
