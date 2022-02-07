from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import  models, schemas, oauth2
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from typing import List, Optional

router=APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.get("/",response_model=List[schemas.PostResponseOut])
def get_posts(db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user),limit: int=10,skip:int =0,search:Optional[str]=""):
    # cursor.execute("""
    #     SELECT * FROM posts
    # """)
    # posts=cursor.fetchall()
    # print(len(posts))
    print(search)
    # posts=db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    posts=db.query(models.Post,func.count(models.Vote.post_id).label('votes')).join(models.Vote,models.Vote.post_id==models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()  
    # print(results)

    return posts

@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.PostResponse)
def create_posts(post:schemas.PostCreate,db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    # cursor.execute("""
    #     INSERT INTO posts (title, content, published)
    #     VALUES (%s,%s,%s)
    #     RETURNING * 
    # """,(post.title,post.content,post.published))
    # new_post=cursor.fetchone()
    # conn.commit()
    print(f'The current user id: {current_user.id}')
    new_post=models.Post(owner_id=current_user.id,**post.dict())
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.get("/{id}",response_model=schemas.PostResponseOut)
def get_post(id:int, db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    
    # cursor.execute("""
    #     SELECT * 
    #     FROM posts
    #     WHERE id=%s
    # """,(str(id),))
    # post=cursor.fetchone()

    # post=db.query(models.Post).filter(models.Post.id==id).first()
    
    post=db.query(models.Post,func.count(models.Vote.post_id).label('votes')).join(models.Vote,models.Vote.post_id==models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id==id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"message with id {id} was not found")
       
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):

    # cursor.execute("""
    #     DELETE FROM posts 
    #     WHERE id=%s
    #     RETURNING *
    # """,(str(id),))

    post=db.query(models.Post).filter(models.Post.id==id)

    if post.first()==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")

    if post.first().owner_id !=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to perform requested action")

    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}",response_model=schemas.PostResponse)
def update_post(id:int, post: schemas.PostCreate,db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):

    # cursor.execute("""
    #     UPDATE posts 
    #     SET title=%s, content=%s, published=%s
    #     WHERE ID=%s
    #     RETURNING *
    # """,(post.title,post.content,post.published,str(id)))

    # Still to add - how to check if user already exists

    post_query=db.query(models.Post).filter(models.Post.id==id)

    print(f'The current user id: {current_user.id}')

    if post_query.first().owner_id !=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to perform requested action")

    if post_query.first()==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")

    print(post.dict())
    post_query.update(post.dict(),synchronize_session=False)
    db.commit()
    return post_query.first()